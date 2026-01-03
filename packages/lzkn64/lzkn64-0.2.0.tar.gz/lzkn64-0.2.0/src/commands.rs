use crate::constants::*;
use crate::error::Lzkn64Error;
use crate::io::ByteReader;

/// Represents a single operation.
#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum Command {
    /// Copy bytes from the output buffer (sliding window).
    SlidingWindow { offset: usize, length: usize },

    /// Copy bytes directly from the input stream.
    Raw { length: usize },

    /// Repeat a byte value (run-length encoding).
    Rle { value: u8, length: usize },
}

impl Command {
    /// Decodes the next command from the reader.
    ///
    /// Returns `Ok(Some(Command))` if a command was successfully read.
    /// Returns `Ok(None)` if the reader is empty.
    /// Returns `Err` if the data is invalid or truncated.
    pub fn decode(reader: &mut ByteReader) -> Result<Option<Self>, Lzkn64Error> {
        if reader.is_empty() {
            return Ok(None);
        }

        let cmd_byte = reader.read_u8()?;

        // Sliding Window Copy (0x00 - 0x7F)
        if cmd_byte <= COMMAND_SLIDING_WINDOW_COPY_END {
            let next_byte = reader.read_u8()?;

            let length = (((cmd_byte & COMMAND_SLIDING_WINDOW_COPY_LENGTH_MASK) >> 2) as usize)
                + LZKN64_LENGTH_BIAS;
            let offset_hi = (cmd_byte & COMMAND_SLIDING_WINDOW_COPY_OFFSET_HI_MASK) as usize;
            let offset_lo = next_byte as usize;
            let offset = (offset_hi << 8) | offset_lo;

            let offset = offset & COMMAND_SLIDING_WINDOW_COPY_OFFSET_MAX;

            return Ok(Some(Command::SlidingWindow { offset, length }));
        }

        // Raw Copy (0x80 - 0x9F)
        if cmd_byte >= COMMAND_RAW_COPY_START && cmd_byte <= COMMAND_RAW_COPY_END {
            let length = (cmd_byte & COMMAND_RAW_COPY_LENGTH_MASK) as usize;

            return Ok(Some(Command::Raw { length }));
        }

        // RLE Short Any (0xC0 - 0xDF)
        if cmd_byte >= COMMAND_RLE_SHORT_ANY_START && cmd_byte <= COMMAND_RLE_SHORT_ANY_END {
            let length =
                ((cmd_byte & COMMAND_RLE_SHORT_ANY_LENGTH_MASK) as usize) + LZKN64_LENGTH_BIAS;
            let value = reader.read_u8()?;

            return Ok(Some(Command::Rle { value, length }));
        }

        // RLE Short Zero (0xE0 - 0xFE)
        if cmd_byte >= COMMAND_RLE_SHORT_ZERO_START && cmd_byte <= COMMAND_RLE_SHORT_ZERO_END {
            let length =
                ((cmd_byte & COMMAND_RLE_SHORT_ZERO_LENGTH_MASK) as usize) + LZKN64_LENGTH_BIAS;

            return Ok(Some(Command::Rle { value: 0, length }));
        }

        // RLE Long Zero (0xFF)
        if cmd_byte == COMMAND_RLE_LONG_ZERO {
            let len_byte = reader.read_u8()?;
            let length =
                ((len_byte & COMMAND_RLE_LONG_ZERO_LENGTH_MASK) as usize) + LZKN64_LENGTH_BIAS;

            return Ok(Some(Command::Rle { value: 0, length }));
        }

        Err(Lzkn64Error::CorruptData(format!(
            "Unknown command byte: {:#02X}",
            cmd_byte
        )))
    }

    /// Encodes the command into the output buffer.
    pub fn encode(&self, output: &mut Vec<u8>) -> Result<(), Lzkn64Error> {
        match *self {
            Command::SlidingWindow { offset, length } => {
                if length < LZKN64_LENGTH_BIAS || length > SLIDING_WINDOW_COPY_MAX_LENGTH {
                    return Err(Lzkn64Error::CompressionError(format!(
                        "Invalid sliding window length: {}",
                        length
                    )));
                }
                if offset > COMMAND_SLIDING_WINDOW_COPY_OFFSET_MAX {
                    return Err(Lzkn64Error::CompressionError(format!(
                        "Invalid sliding window offset: {}",
                        offset
                    )));
                }

                let b1 = COMMAND_SLIDING_WINDOW_COPY_START
                    | (((length - LZKN64_LENGTH_BIAS) as u8) << 2)
                        & COMMAND_SLIDING_WINDOW_COPY_LENGTH_MASK
                    | (((offset >> 8) as u8) & COMMAND_SLIDING_WINDOW_COPY_OFFSET_HI_MASK);
                let b2 = (offset as u8) & COMMAND_SLIDING_WINDOW_COPY_OFFSET_LO_MASK;

                output.push(b1);
                output.push(b2);
            }
            Command::Raw { length } => {
                if length > RAW_COPY_MAX_LENGTH {
                    return Err(Lzkn64Error::CompressionError(format!(
                        "Invalid raw length: {}",
                        length
                    )));
                }

                // Caller is responsible for writing the raw data after this command byte
                output.push(COMMAND_RAW_COPY_START | (length as u8 & COMMAND_RAW_COPY_LENGTH_MASK));
            }
            Command::Rle { value, length } => {
                if value == 0 {
                    if length < LZKN64_LENGTH_BIAS {
                        return Err(Lzkn64Error::CompressionError(format!(
                            "Invalid run-length encoding length: {}",
                            length
                        )));
                    }

                    if length < RLE_SHORT_MAX_LENGTH {
                        output.push(
                            COMMAND_RLE_SHORT_ZERO_START
                                | ((length - LZKN64_LENGTH_BIAS) as u8
                                    & COMMAND_RLE_SHORT_ZERO_LENGTH_MASK),
                        );
                    } else if length <= RLE_LONG_MAX_LENGTH {
                        output.push(COMMAND_RLE_LONG_ZERO);
                        output.push(
                            (length - LZKN64_LENGTH_BIAS) as u8 & COMMAND_RLE_LONG_ZERO_LENGTH_MASK,
                        );
                    } else {
                        return Err(Lzkn64Error::CompressionError(format!(
                            "Run-length encoding length (zero value) too large: {}",
                            length
                        )));
                    }
                } else {
                    if length < LZKN64_LENGTH_BIAS || length > RLE_SHORT_MAX_LENGTH {
                        return Err(Lzkn64Error::CompressionError(format!(
                            "Invalid run-length encoding (any value) length: {}",
                            length
                        )));
                    }
                    
                    output.push(
                        COMMAND_RLE_SHORT_ANY_START
                            | ((length - LZKN64_LENGTH_BIAS) as u8
                                & COMMAND_RLE_SHORT_ANY_LENGTH_MASK),
                    );
                    output.push(value);
                }
            }
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_decode_sw() {
        // Length 3 (0 encoded), Offset 1
        // 3 - 2 = 1 -> << 2 -> 4 (0x04)
        // Offset 1 -> Hi 0, Lo 1
        // Byte 1: 0x00 | 0x04 | 0x00 = 0x04
        // Byte 2: 0x01
        let data = [0x04, 0x01];
        let mut reader = ByteReader::new(&data);
        let cmd = Command::decode(&mut reader).unwrap().unwrap();
        assert_eq!(
            cmd,
            Command::SlidingWindow {
                offset: 1,
                length: 3
            }
        );
    }

    #[test]
    fn test_encode_rle_zero() {
        let mut out = Vec::new();
        let cmd = Command::Rle {
            value: 0,
            length: 4,
        };
        cmd.encode(&mut out).unwrap();
        // 4 - 2 = 2. Short Zero Start 0xE0. 0xE0 | 2 = 0xE2
        assert_eq!(out, vec![0xE2]);
    }
}
