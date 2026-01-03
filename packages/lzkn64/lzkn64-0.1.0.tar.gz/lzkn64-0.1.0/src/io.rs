use crate::error::Lzkn64Error;
use std::convert::TryInto;

/// A lightweight, safe wrapper around a byte slice for sequential reading.
///
/// `ByteReader` tracks the current position and performs automatic bounds checking,
/// returning `Lzkn64Error::InputOverflow` if a read extends beyond the end of the slice.
#[derive(Debug, Clone)]
pub struct ByteReader<'a> {
    data: &'a [u8],
    pos: usize,
}

impl<'a> ByteReader<'a> {
    /// Creates a new `ByteReader` for the given data slice.
    #[inline]
    pub fn new(data: &'a [u8]) -> Self {
        Self { data, pos: 0 }
    }

    /// Returns the total length of the underlying data.
    #[inline]
    #[allow(dead_code)]
    pub fn len(&self) -> usize {
        self.data.len()
    }

    /// Returns `true` if the reader has reached the end of the data.
    #[inline]
    pub fn is_empty(&self) -> bool {
        self.pos >= self.data.len()
    }

    /// Returns the current read position.
    #[inline]
    #[allow(dead_code)]
    pub fn pos(&self) -> usize {
        self.pos
    }

    /// Returns the number of bytes remaining to be read.
    #[inline]
    pub fn remaining(&self) -> usize {
        self.data.len().saturating_sub(self.pos)
    }

    /// Sets the current position.
    ///
    /// # Errors
    /// Returns `Lzkn64Error::InputOverflow` if `pos` is out of bounds.
    #[allow(dead_code)]
    pub fn seek(&mut self, pos: usize) -> Result<(), Lzkn64Error> {
        if pos > self.data.len() {
            return Err(Lzkn64Error::InputOverflow);
        }
        self.pos = pos;
        Ok(())
    }

    /// Reads a single byte and advances the position.
    /// 
    /// # Errors
    /// Returns `Lzkn64Error::InputOverflow` if attempting to read out of bounds.
    #[inline]
    pub fn read_u8(&mut self) -> Result<u8, Lzkn64Error> {
        if self.pos >= self.data.len() {
            return Err(Lzkn64Error::InputOverflow);
        }
        let byte = self.data[self.pos];
        self.advance(1)?;
        Ok(byte)
    }

    /// Returns the next byte without advancing the position.
    /// 
    /// # Errors
    /// Returns `Lzkn64Error::InputOverflow` if attempting to read out of bounds.
    #[inline]
    #[allow(dead_code)]
    pub fn peek_u8(&self) -> Result<u8, Lzkn64Error> {
        if self.pos >= self.data.len() {
            return Err(Lzkn64Error::InputOverflow);
        }
        Ok(self.data[self.pos])
    }

    /// Reads a 32-bit big-endian unsigned integer and advances the position by 4.
    pub fn read_be32(&mut self) -> Result<u32, Lzkn64Error> {
        let slice = self.read_slice(4)?;
        let array: [u8; 4] = slice.try_into().unwrap();
        Ok(u32::from_be_bytes(array))
    }

    /// Reads a 32-bit little-endian unsigned integer and advances the position by 4.
    #[allow(dead_code)]
    pub fn read_le32(&mut self) -> Result<u32, Lzkn64Error> {
        let slice = self.read_slice(4)?;
        let array: [u8; 4] = slice.try_into().unwrap();
        Ok(u32::from_le_bytes(array))
    }

    /// Reads `len` bytes as a sub-slice and advances the position.
    ///
    /// The returned slice borrows from the original data.
    /// 
    /// # Errors
    /// Returns `Lzkn64Error::InputOverflow` if attempting to read out of bounds.
    #[allow(dead_code)]
    pub fn read_slice(&mut self, len: usize) -> Result<&'a [u8], Lzkn64Error> {
        let end = self
            .pos
            .checked_add(len)
            .ok_or(Lzkn64Error::InputOverflow)?;
        if end > self.data.len() {
            return Err(Lzkn64Error::InputOverflow);
        }
        let slice = &self.data[self.pos..end];
        self.pos = end;
        Ok(slice)
    }

    /// Advances the position by `count` bytes without returning data.
    /// 
    /// # Errors
    /// Returns `Lzkn64Error::InputOverflow` if advancing would go out of bounds.
    #[inline]
    pub fn advance(&mut self, count: usize) -> Result<(), Lzkn64Error> {
        let new_pos = self
            .pos
            .checked_add(count)
            .ok_or(Lzkn64Error::InputOverflow)?;
        if new_pos > self.data.len() {
            return Err(Lzkn64Error::InputOverflow);
        }
        self.pos = new_pos;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_read_u8() {
        let data = [0x10, 0x20, 0x30];
        let mut reader = ByteReader::new(&data);

        assert_eq!(reader.read_u8().unwrap(), 0x10);
        assert_eq!(reader.read_u8().unwrap(), 0x20);
        assert_eq!(reader.read_u8().unwrap(), 0x30);
        assert!(matches!(
            reader.read_u8().unwrap_err(),
            Lzkn64Error::InputOverflow
        ));
    }

    #[test]
    fn test_peek_u8() {
        let data = [0xAA, 0xBB];
        let mut reader = ByteReader::new(&data);

        assert_eq!(reader.peek_u8().unwrap(), 0xAA);
        assert_eq!(reader.pos(), 0);
        assert_eq!(reader.read_u8().unwrap(), 0xAA);
        assert_eq!(reader.pos(), 1);
    }

    #[test]
    fn test_read_be32() {
        let data = [0x01, 0x02, 0x03, 0x04, 0x05];
        let mut reader = ByteReader::new(&data);

        assert_eq!(reader.read_be32().unwrap(), 0x01020304);
        assert_eq!(reader.pos(), 4);
        assert!(matches!(
            reader.read_be32().unwrap_err(),
            Lzkn64Error::InputOverflow
        ));
    }

    #[test]
    fn test_read_slice() {
        let data = [1, 2, 3, 4, 5];
        let mut reader = ByteReader::new(&data);

        assert_eq!(reader.read_slice(2).unwrap(), &[1, 2]);
        assert_eq!(reader.read_slice(3).unwrap(), &[3, 4, 5]);
        assert!(matches!(
            reader.read_slice(1).unwrap_err(),
            Lzkn64Error::InputOverflow
        ));
    }

    #[test]
    fn test_overflow_checks() {
        let data = [0u8; 10];
        let mut reader = ByteReader::new(&data);

        assert!(matches!(
            reader.advance(usize::MAX).unwrap_err(),
            Lzkn64Error::InputOverflow
        ));
    }
}
