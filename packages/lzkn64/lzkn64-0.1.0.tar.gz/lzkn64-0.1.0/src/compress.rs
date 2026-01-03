use crate::commands::Command;
use crate::constants::*;
use crate::error::Lzkn64Error;

// Compression parameters
const MIN_SW_MATCH: usize = 4;
const MIN_RLE_LENGTH: usize = 3;
const MIN_RLE_ZERO_LENGTH: usize = 2;
const RLE_SHORT_ANY_MAX_LENGTH: usize = RLE_SHORT_MAX_LENGTH - 1;
const PREFER_SW: bool = false;

struct MatchCandidates {
    sw: Option<(usize, usize)>, // (offset, length)
    rle: Option<(u8, usize)>,   // (value, length)
}

pub fn compress(input: &[u8]) -> Result<Vec<u8>, Lzkn64Error> {
    if input.is_empty() {
        return Err(Lzkn64Error::InvalidSize);
    }

    // Estimate capacity: input size + raw copy overhead + header
    let mut output = Vec::with_capacity(input.len() + (input.len() / RAW_COPY_MAX_LENGTH + 1) + LZKN64_HEADER_SIZE);

    // Reserve header space (4 bytes)
    output.extend_from_slice(&[0, 0, 0, 0]);

    compress_chunk(input, &mut output)?;

    let chunk_size = output.len();

    // Validate chunk size
    if chunk_size > LZKN64_CHUNK_SIZE_MASK as usize {
        return Err(Lzkn64Error::OutputOverflow);
    }

    // Write chunk header
    // (plane_count = 1 (meaning bits 31-28 are equal to 0)) | chunk size
    let chunk_header = chunk_size as u32;
    let chunk_header_bytes = chunk_header.to_be_bytes();
    output[..4].copy_from_slice(&chunk_header_bytes);

    Ok(output)
}

fn compress_chunk(input: &[u8], output: &mut Vec<u8>) -> Result<(), Lzkn64Error> {
    let mut pos = 0;
    let mut last_processed = 0;

    while pos < input.len() {
        let matches = find_matches(input, pos);
        let command = select_command(&matches);

        // Determine if we need to flush raw bytes.
        // We flush if:
        // 1. We found a command (and want to emit pending raw bytes before it)
        // 2. We have accumulated enough raw bytes to fill a max-size raw block
        // 3. We are at the end of the input (handled in loop termination)
        let should_flush_raw = command.is_some() || (pos - last_processed >= RAW_COPY_MAX_LENGTH);

        if should_flush_raw {
            emit_pending_raw_copy(input, output, &mut last_processed, pos)?;
        }

        if let Some(cmd) = command {
            match cmd {
                Command::SlidingWindow { offset: _, length } => {
                    cmd.encode(output)?;
                    pos += length;
                }
                Command::Rle { value: _, length } => {
                    cmd.encode(output)?;
                    pos += length;
                }
                _ => {
                    return Err(Lzkn64Error::CompressionError(
                        "Unexpected command selection".to_string(),
                    ));
                }
            }

            last_processed = pos;
        } else {
            // No match found, advance position to accumulate raw bytes
            pos += 1;
        }
    }

    // Flush any remaining raw bytes at the end
    emit_pending_raw_copy(input, output, &mut last_processed, input.len())?;

    Ok(())
}

fn find_matches(input: &[u8], pos: usize) -> MatchCandidates {
    let mut candidates = MatchCandidates {
        sw: None,
        rle: None,
    };

    // --- Sliding Window Search ---
    let sw_max_len = std::cmp::min(SLIDING_WINDOW_COPY_MAX_LENGTH, input.len() - pos);
    let sw_max_offset = std::cmp::min(SLIDING_WINDOW_SIZE, pos);

    if sw_max_len >= MIN_SW_MATCH {
        // Brute force search.
        // We want the longest match. If equal length, prefer smaller offset (closer)
        // Iterating 1..=sw_max_offset gives us smaller offsets first

        let mut best_sw_len = 0;
        let mut best_sw_offset = 0;

        for offset in 1..=sw_max_offset {
            let mut len = 0;
            let src_start = pos - offset;

            // Quick check first byte to skip unnecessary comparisons
            if input[src_start] != input[pos] {
                continue;
            }

            // Compare up to sw_max_len bytes
            for i in 0..sw_max_len {
                if input[src_start + i] == input[pos + i] {
                    len += 1;
                } else {
                    break;
                }
            }
            
            // Update best match if longer
            if len > best_sw_len {
                best_sw_len = len;
                best_sw_offset = offset;

                // If we hit the max possible length, we can stop early because
                // we are iterating from smallest offset (best) to largest
                if len == sw_max_len {
                    break;
                }
            }
        }

        if best_sw_len >= MIN_SW_MATCH {
            candidates.sw = Some((best_sw_offset, best_sw_len));
        }
    }

    // --- Run Length Encoding Search ---
    let mut rle_max_len = std::cmp::min(RLE_LONG_MAX_LENGTH, input.len() - pos);

    // Apply block alignment quirk
    if rle_max_len > RLE_SHORT_MAX_LENGTH {
        for i in (RLE_SHORT_MAX_LENGTH + 1)..=rle_max_len {
            let block_pos = (pos + i) & LZKN64_BLOCK_MASK;

            // Limit the maximum length to the end of the current block
            if block_pos % LZKN64_BLOCK_ALIGNMENT == RLE_SHORT_MAX_LENGTH {
                rle_max_len = i;
                break;
            }
        }
    }

    let val = input[pos];

    // Run-length encoding length is more limited for non-zero values
    let rle_window_len = if val != 0 {
        std::cmp::min(rle_max_len, RLE_SHORT_ANY_MAX_LENGTH)
    } else {
        rle_max_len
    };

    // Find run-length
    let mut rle_len = 0;
    for i in 0..rle_window_len {
        if input[pos + i] == val {
            rle_len += 1;
        } else {
            break;
        }
    }

    // Validate minimum lengths
    if (val == 0 && rle_len >= MIN_RLE_ZERO_LENGTH) || (val != 0 && rle_len >= MIN_RLE_LENGTH) {
        candidates.rle = Some((val, rle_len));
    }

    candidates
}

fn select_command(matches: &MatchCandidates) -> Option<Command> {
    let use_sw = matches.sw.is_some();
    let use_rle = matches.rle.is_some();

    if !use_sw && !use_rle {
        return None;
    }

    // Decide preference
    let prefer_sw_match = if use_sw && use_rle {
        let sw_len = matches.sw.unwrap().1;
        let rle_len = matches.rle.unwrap().1;

        if PREFER_SW {
            sw_len >= rle_len // Prefer sliding window if equal
        } else {
            sw_len > rle_len // Prefer run-length encoding if equal
        }
    } else {
        use_sw
    };

    // Return selected command
    if prefer_sw_match {
        let (offset, length) = matches.sw.unwrap();
        Some(Command::SlidingWindow { offset, length })
    } else {
        let (value, length) = matches.rle.unwrap();
        Some(Command::Rle { value, length })
    }
}

fn emit_pending_raw_copy(
    input: &[u8],
    output: &mut Vec<u8>,
    last_processed: &mut usize,
    current_pos: usize,
) -> Result<(), Lzkn64Error> {
    let mut raw_length = current_pos - *last_processed;

    while raw_length > 0 {
        let chunk_size = std::cmp::min(raw_length, RAW_COPY_MAX_LENGTH);

        // Output raw copy command
        let cmd = Command::Raw { length: chunk_size };
        cmd.encode(output)?;

        // Output raw bytes.
        output.extend_from_slice(&input[*last_processed..*last_processed + chunk_size]);

        // Update last processed position and remaining length
        *last_processed += chunk_size;
        raw_length -= chunk_size;
    }

    Ok(())
}
