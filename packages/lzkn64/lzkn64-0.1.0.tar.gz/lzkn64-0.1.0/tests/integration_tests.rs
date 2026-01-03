use lzkn64::{compress, decompress};

#[test]
fn test_round_trip_simple() {
    let data = b"Hello world! Hello world! Hello world!";
    let compressed = compress(data).expect("Compression failed");
    let decompressed = decompress(&compressed).expect("Decompression failed");
    assert_eq!(data.as_slice(), decompressed.as_slice());
}

#[test]
fn test_round_trip_zeros() {
    let data = vec![0u8; 1000];
    let compressed = compress(&data).expect("Compression failed");
    let decompressed = decompress(&compressed).expect("Decompression failed");
    assert_eq!(data, decompressed);
}

#[test]
fn test_round_trip_repeated() {
    let data = vec![0xAAu8; 1000];
    let compressed = compress(&data).expect("Compression failed");
    let decompressed = decompress(&compressed).expect("Decompression failed");
    assert_eq!(data, decompressed);
}

#[test]
fn test_round_trip_random_ish() {
    let mut data = Vec::with_capacity(10000);
    for i in 0..10000 {
        data.push((i % 256) as u8);
    }

    // Add some repetition to ensure compression happens
    for _ in 0..100 {
        data.extend_from_slice(b"repeated pattern here ");
    }

    let compressed = compress(&data).expect("Compression failed");
    let decompressed = decompress(&compressed).expect("Decompression failed");
    assert_eq!(data, decompressed);
}

#[test]
fn test_large_file() {
    // 1MB of data
    let mut data = Vec::with_capacity(1024 * 1024);
    for i in 0..(1024 * 1024) {
        data.push(((i * 7) % 256) as u8);
    }

    let compressed = compress(&data).expect("Compression failed");
    let decompressed = decompress(&compressed).expect("Decompression failed");
    assert_eq!(data, decompressed);
}

#[test]
fn test_invalid_header() {
    let data = vec![0, 0, 0]; // Too short
    assert!(decompress(&data).is_err());
}
