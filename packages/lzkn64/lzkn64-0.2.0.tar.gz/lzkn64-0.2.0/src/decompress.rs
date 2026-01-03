use crate::commands::Command;
use crate::constants::*;
use crate::error::Lzkn64Error;
use crate::io::ByteReader;

pub fn decompress(input: &[u8]) -> Result<Vec<u8>, Lzkn64Error> {
    if input.len() < LZKN64_HEADER_SIZE {
        return Err(Lzkn64Error::InvalidSize);
    }

    let mut reader = ByteReader::new(input);
    let mut output = Vec::with_capacity(input.len() * 3); // Estimate capacity

    while !reader.is_empty() {
        // Check for header availability
        if reader.remaining() < LZKN64_HEADER_SIZE {
            break; // No more complete chunks
        }

        // Read chunk header
        let chunk_header = reader.read_be32()?;

        let plane_count = ((chunk_header >> LZKN64_PLANE_COUNT_SHIFT) & 0x0F) + 1;
        if plane_count > 1 {
            return Err(Lzkn64Error::UnsupportedInterleaved);
        }

        let chunk_size = (chunk_header & LZKN64_CHUNK_SIZE_MASK) as usize;

        // Validate chunk size
        // We know we read 4 bytes, so chunk_size must be at least 4
        if chunk_size < LZKN64_HEADER_SIZE {
            return Err(Lzkn64Error::InvalidHeader);
        }

        // chunk_size includes the header (4 bytes) we just read
        // We need to verify that we have enough bytes remaining in the input for the rest (body) of the chunk
        let body_size = chunk_size - LZKN64_HEADER_SIZE;
        if reader.remaining() < body_size {
            return Err(Lzkn64Error::InvalidHeader);
        }

        let chunk_body = reader.read_slice(body_size)?;

        if body_size == 0 {
            continue; // Empty chunk
        }

        decompress_chunk(chunk_body, &mut output)?;
    }

    Ok(output)
}

fn decompress_chunk(chunk_data: &[u8], output: &mut Vec<u8>) -> Result<(), Lzkn64Error> {
    let mut reader = ByteReader::new(chunk_data);

    while !reader.is_empty() {
        let command = Command::decode(&mut reader)?;

        match command {
            Some(Command::SlidingWindow { offset, length }) => {
                if offset == 0 || offset > output.len() {
                    return Err(Lzkn64Error::CorruptData(format!(
                        "Invalid backreference offset: {}",
                        offset
                    )));
                }

                let start_idx = output.len() - offset;
                for i in 0..length {
                    let val = output[start_idx + i];
                    output.push(val);
                }
            }
            Some(Command::Raw { length }) => {
                let bytes = reader.read_slice(length)?;
                output.extend_from_slice(bytes);
            }
            Some(Command::Rle { value, length }) => {
                for _ in 0..length {
                    output.push(value);
                }
            }
            None => break,
        }
    }
    Ok(())
}
