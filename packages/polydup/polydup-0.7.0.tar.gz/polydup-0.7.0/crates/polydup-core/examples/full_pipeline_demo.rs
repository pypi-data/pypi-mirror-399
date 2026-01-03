//! Full pipeline demo: Parse → Normalize → Hash → Detect Duplicates

use dupe_core::Scanner;
use std::fs;

fn main() -> anyhow::Result<()> {
    println!("=== PolyDup Complete Pipeline Demo ===\n");

    // Create test files with duplicate code
    let temp_dir = std::env::temp_dir().join("polydup_demo");
    fs::create_dir_all(&temp_dir)?;

    // Create two Rust files with similar functions
    let file1 = temp_dir.join("calc1.rs");
    fs::write(
        &file1,
        r#"
fn add_numbers(a: i32, b: i32) -> i32 {
    let result = a + b;
    println!("Adding {} + {}", a, b);
    result
}

fn multiply_numbers(x: i32, y: i32) -> i32 {
    let product = x * y;
    println!("Multiplying {} * {}", x, y);
    product
}
"#,
    )?;

    let file2 = temp_dir.join("calc2.rs");
    fs::write(
        &file2,
        r#"
fn sum(first: i32, second: i32) -> i32 {
    let total = first + second;
    println!("Adding {} + {}", first, second);
    total
}

fn product(num1: i32, num2: i32) -> i32 {
    let result = num1 * num2;
    println!("Multiplying {} * {}", num1, num2);
    result
}
"#,
    )?;

    // Create a Python file with a duplicate
    let file3 = temp_dir.join("math.py");
    fs::write(
        &file3,
        r#"
def add_values(x, y):
    result = x + y
    print(f"Adding {x} + {y}")
    return result

def unique_function():
    print("This is unique")
    return 42
"#,
    )?;

    println!("Created test files in: {:?}\n", temp_dir);

    // Run scanner
    let scanner = Scanner::with_config(5, 0.8)?;
    let report = scanner.scan(vec![temp_dir.clone()])?;

    // Display results
    println!("📊 Scan Report:");
    println!("  Files scanned: {}", report.files_scanned);
    println!("  Functions analyzed: {}", report.functions_analyzed);
    println!("  Duplicates found: {}", report.duplicates.len());
    println!("  \n📈 Statistics:");
    println!("  Total tokens: {}", report.stats.total_tokens);
    println!("  Unique hashes: {}", report.stats.unique_hashes);
    println!("  Duration: {}ms\n", report.stats.duration_ms);

    if !report.duplicates.is_empty() {
        println!("Detected Duplicates:");
        for (idx, dup) in report.duplicates.iter().enumerate() {
            println!(
                "  {}. {} ↔️ {}",
                idx + 1,
                dup.file1.split('/').next_back().unwrap_or(&dup.file1),
                dup.file2.split('/').next_back().unwrap_or(&dup.file2),
            );
            println!(
                "     Similarity: {:.1}% | Hash: {:#x}",
                dup.similarity * 100.0,
                dup.hash
            );
        }
    } else {
        println!("✅ No duplicates detected!");
    }

    // Cleanup
    fs::remove_dir_all(&temp_dir)?;
    println!("\n🧹 Cleaned up test files");

    Ok(())
}
