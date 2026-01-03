//! Integration tests for ignore functionality

use dupe_core::{compute_duplicate_id, FileRange, IgnoreEntry, IgnoreManager, Scanner};
use std::fs;
use std::path::PathBuf;
use tempfile::TempDir;

/// Helper to create a test file
fn create_test_file(dir: &TempDir, name: &str, content: &str) -> PathBuf {
    let path = dir.path().join(name);
    fs::write(&path, content).unwrap();
    path
}

#[test]
fn test_ignore_manager_with_scanner_api() {
    // Create temporary directory with test files
    let temp_dir = TempDir::new().unwrap();

    let file1 = create_test_file(
        &temp_dir,
        "test1.js",
        r#"
function calculateSum(a, b) {
    let result = 0;
    for (let i = 0; i < 100; i++) {
        result += i;
    }
    result += a + b;
    console.log("Processing");
    console.log("More processing");
    console.log("Even more");
    let temp1 = result * 2;
    let temp2 = temp1 + 10;
    let temp3 = temp2 - 5;
    let temp4 = temp3 * 3;
    let temp5 = temp4 / 2;
    let temp6 = temp5 + 100;
    let temp7 = temp6 - 50;
    let temp8 = temp7 * 4;
    let temp9 = temp8 / 3;
    let temp10 = temp9 + 200;
    return temp10;
}
        "#,
    );

    let file2 = create_test_file(
        &temp_dir,
        "test2.js",
        r#"
function computeTotal(x, y) {
    let sum = 0;
    for (let j = 0; j < 100; j++) {
        sum += j;
    }
    sum += x + y;
    console.log("Processing");
    console.log("More processing");
    console.log("Even more");
    let value1 = sum * 2;
    let value2 = value1 + 10;
    let value3 = value2 - 5;
    let value4 = value3 * 3;
    let value5 = value4 / 2;
    let value6 = value5 + 100;
    let value7 = value6 - 50;
    let value8 = value7 * 4;
    let value9 = value8 / 3;
    let value10 = value9 + 200;
    return value10;
}
        "#,
    );

    // First scan without ignore manager
    let scanner1 = Scanner::new();
    let report1 = scanner1.scan(vec![file1.clone(), file2.clone()]).unwrap();

    assert!(
        !report1.duplicates.is_empty(),
        "Should detect duplicates in test files"
    );

    // Test that we can create a scanner with an ignore manager
    // (the actual filtering will be tested with more complex integration)
    let ignore_manager = IgnoreManager::new(temp_dir.path());
    let scanner2 = Scanner::new().with_ignore_manager(ignore_manager);
    let report2 = scanner2.scan(vec![file1, file2]).unwrap();

    // With empty ignore manager, should get same results
    assert_eq!(
        report1.duplicates.len(),
        report2.duplicates.len(),
        "Empty ignore manager should not filter any duplicates"
    );
}

#[test]
fn test_ignore_manager_persistence() {
    // Create temporary directory
    let temp_dir = TempDir::new().unwrap();

    // Create and save an ignore entry
    let mut manager1 = IgnoreManager::new(temp_dir.path());
    let entry = IgnoreEntry {
        id: "test-id-123".to_string(),
        files: vec![FileRange {
            file: PathBuf::from("test.js"),
            start_line: 10,
            end_line: 20,
        }],
        reason: "False positive".to_string(),
        added_by: "developer".to_string(),
        added_at: chrono::Utc::now(),
    };

    manager1.add_ignore(entry.clone());
    manager1.save().unwrap();
    assert!(manager1.is_ignored("test-id-123"));

    // Load ignore file again
    let mut manager2 = IgnoreManager::new(temp_dir.path());
    manager2.load().unwrap();
    assert!(
        manager2.is_ignored("test-id-123"),
        "Should persist ignored IDs"
    );

    let entries = manager2.list_ignores();
    assert_eq!(entries.len(), 1);
    assert_eq!(entries[0].id, "test-id-123");
    assert_eq!(entries[0].reason, "False positive");
}

#[test]
fn test_compute_duplicate_id_consistency() {
    // Same tokens should produce same ID
    let tokens1 = vec![
        "$$ID".to_string(),
        "=".to_string(),
        "$$ID".to_string(),
        "+".to_string(),
        "$$ID".to_string(),
    ];

    let tokens2 = vec![
        "$$ID".to_string(),
        "=".to_string(),
        "$$ID".to_string(),
        "+".to_string(),
        "$$ID".to_string(),
    ];

    let id1 = compute_duplicate_id(&tokens1);
    let id2 = compute_duplicate_id(&tokens2);

    assert_eq!(id1, id2, "Same tokens should produce same ID");

    // Different tokens should produce different IDs
    let tokens3 = vec![
        "$$ID".to_string(),
        "=".to_string(),
        "$$ID".to_string(),
        "*".to_string(), // Different operator
        "$$ID".to_string(),
    ];

    let id3 = compute_duplicate_id(&tokens3);
    assert_ne!(id1, id3, "Different tokens should produce different IDs");
}

#[test]
fn test_ignore_manager_empty() {
    // Create temporary directory
    let temp_dir = TempDir::new().unwrap();

    // Create empty ignore manager
    let manager = IgnoreManager::new(temp_dir.path());

    // Should not be ignored
    assert!(!manager.is_ignored("any-id"));
    assert_eq!(manager.list_ignores().len(), 0);
}

#[test]
fn test_ignore_manager_remove() {
    // Create temporary directory
    let temp_dir = TempDir::new().unwrap();

    // Create manager and add entry
    let mut manager = IgnoreManager::new(temp_dir.path());
    let entry = IgnoreEntry {
        id: "test-id-456".to_string(),
        files: vec![],
        reason: "Test".to_string(),
        added_by: "test".to_string(),
        added_at: chrono::Utc::now(),
    };

    manager.add_ignore(entry);
    assert!(manager.is_ignored("test-id-456"));

    // Remove entry
    let removed = manager.remove_ignore("test-id-456");
    assert!(removed, "Should return true when entry exists");
    assert!(!manager.is_ignored("test-id-456"));

    // Try to remove again
    let removed_again = manager.remove_ignore("test-id-456");
    assert!(
        !removed_again,
        "Should return false when entry doesn't exist"
    );
}
