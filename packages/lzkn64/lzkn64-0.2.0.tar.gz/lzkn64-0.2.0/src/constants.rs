pub const LZKN64_HEADER_SIZE: usize = 4;
pub const LZKN64_CHUNK_SIZE_MASK: u32 = 0xFFFFFFF;
pub const LZKN64_PLANE_COUNT_SHIFT: u32 = 28;

pub const LZKN64_BLOCK_ALIGNMENT: usize = 0x400;
pub const LZKN64_BLOCK_MASK: usize = 0xFFF;

pub const LZKN64_LENGTH_BIAS: usize = 2;

// Sliding window parameters
pub const SLIDING_WINDOW_SIZE: usize = 0x3DF;
pub const SLIDING_WINDOW_COPY_MAX_LENGTH: usize = 0x1F + LZKN64_LENGTH_BIAS;

// Raw copy parameters
pub const RAW_COPY_MAX_LENGTH: usize = 0x1F;

// Run-length encoding parameters
pub const RLE_SHORT_MAX_LENGTH: usize = 0x1F + LZKN64_LENGTH_BIAS;
pub const RLE_LONG_MAX_LENGTH: usize = 0xFF + LZKN64_LENGTH_BIAS;

// Sliding window copy: 0x00 - 0x7F
pub const COMMAND_SLIDING_WINDOW_COPY_START: u8 = 0x00;
pub const COMMAND_SLIDING_WINDOW_COPY_END: u8 = 0x7F;
pub const COMMAND_SLIDING_WINDOW_COPY_LENGTH_MASK: u8 = 0x7C;
pub const COMMAND_SLIDING_WINDOW_COPY_OFFSET_HI_MASK: u8 = 0x03;
pub const COMMAND_SLIDING_WINDOW_COPY_OFFSET_LO_MASK: u8 = 0xFF;
pub const COMMAND_SLIDING_WINDOW_COPY_OFFSET_MAX: usize = 0x3FF;

// Raw copy: 0x80 - 0x9F
pub const COMMAND_RAW_COPY_START: u8 = 0x80;
pub const COMMAND_RAW_COPY_END: u8 = 0x9F;
pub const COMMAND_RAW_COPY_LENGTH_MASK: u8 = 0x1F;

// RLE Short (Any): 0xC0 - 0xDF
pub const COMMAND_RLE_SHORT_ANY_START: u8 = 0xC0;
pub const COMMAND_RLE_SHORT_ANY_END: u8 = 0xDF;
pub const COMMAND_RLE_SHORT_ANY_LENGTH_MASK: u8 = 0x1F;

// RLE Short (Zero): 0xE0 - 0xFE
pub const COMMAND_RLE_SHORT_ZERO_START: u8 = 0xE0;
pub const COMMAND_RLE_SHORT_ZERO_END: u8 = 0xFE;
pub const COMMAND_RLE_SHORT_ZERO_LENGTH_MASK: u8 = 0x1F;

// RLE Long (Zero): 0xFF
pub const COMMAND_RLE_LONG_ZERO: u8 = 0xFF;
pub const COMMAND_RLE_LONG_ZERO_LENGTH_MASK: u8 = 0xFF;
