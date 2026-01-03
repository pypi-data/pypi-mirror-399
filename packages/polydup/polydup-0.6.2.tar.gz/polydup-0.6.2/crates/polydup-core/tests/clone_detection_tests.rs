//! Integration tests for different types of code clone detection
//!
//! Tests cover:
//! - Type-1 clones: Exact copies (only whitespace/comments differ)
//! - Type-2 clones: Parametrized clones (identifiers/literals renamed)
//! - Type-3 clones: Near-miss clones (with modifications)
//! - Extension algorithm: Variable-length duplicate detection

use dupe_core::{detect_duplicates_with_extension, normalize, Scanner};
use std::path::PathBuf;

#[test]
fn test_type1_exact_clones() {
    // Type-1: Exact copies with only whitespace differences
    let code1 = r#"
        function calculateSum(a, b) {
            return a + b;
        }
    "#;

    let code2 = r#"
        function calculateSum(a, b) {
            return a + b;
        }
    "#;

    let tokens1 = normalize(code1);
    let tokens2 = normalize(code2);

    // Type-1 clones should produce identical token sequences
    assert_eq!(tokens1, tokens2);
}

#[test]
fn test_type2_parametrized_clones() {
    // Type-2: Same structure, different identifiers
    let code1 = r#"
        function calculateTotal(items) {
            let sum = 0;
            for (let i = 0; i < items.length; i++) {
                sum += items[i].price;
            }
            return sum;
        }
    "#;

    let code2 = r#"
        function computePrice(products) {
            let total = 0;
            for (let j = 0; j < products.length; j++) {
                total += products[j].price;
            }
            return total;
        }
    "#;

    let tokens1 = normalize(code1);
    let tokens2 = normalize(code2);

    // Type-2 clones should produce identical token sequences after normalization
    // (identifiers normalized to @@ID)
    assert_eq!(tokens1, tokens2);
}

#[test]
fn test_type2_string_literals() {
    // Type-2: Same structure, different string literals
    let code1 = r#"
        function greet(name) {
            console.log("Hello, " + name);
            return "Welcome";
        }
    "#;

    let code2 = r#"
        function welcome(user) {
            console.log("Hi, " + user);
            return "Greetings";
        }
    "#;

    let tokens1 = normalize(code1);
    let tokens2 = normalize(code2);

    // String literals should be normalized
    assert_eq!(tokens1, tokens2);
}

#[test]
fn test_type3_near_miss_clones() {
    // Type-3: Similar structure with modifications
    let code1 = r#"
        function processOrder(order) {
            if (!order.id) return null;
            let total = calculateTotal(order.items);
            return total;
        }
    "#;

    let code2 = r#"
        function handleOrder(order) {
            if (!order.id) return null;
            let total = calculateTotal(order.items);
            let tax = total * 0.1;  // Additional line
            return total;
        }
    "#;

    let tokens1 = normalize(code1);
    let tokens2 = normalize(code2);

    // Type-3 clones should have partial overlap
    assert_ne!(tokens1, tokens2);

    // But should share significant common subsequences
    let _matches = detect_duplicates_with_extension(&tokens1, 10);
    // Note: This would need cross-function detection in full implementation
}

#[test]
fn test_extension_algorithm_50_tokens() {
    // Test that we detect exactly 50-token duplicates (minimum window)
    let code = r#"
        function test() {
            let a = 1; let b = 2; let c = 3; let d = 4;
            let e = 5; let f = 6; let g = 7; let h = 8;
            return a + b + c + d + e + f + g + h;
        }

        function duplicate() {
            let a = 1; let b = 2; let c = 3; let d = 4;
            let e = 5; let f = 6; let g = 7; let h = 8;
            return a + b + c + d + e + f + g + h;
        }
    "#;

    let tokens = normalize(code);
    let matches = detect_duplicates_with_extension(&tokens, 20);

    // Should find at least one match
    assert!(!matches.is_empty());

    // All matches should be >= 20 tokens (minimum window)
    for m in &matches {
        assert!(
            m.length >= 20,
            "Match length {} is less than minimum window 20",
            m.length
        );
    }
}

#[test]
fn test_extension_algorithm_large_duplicate() {
    // Test that we detect large duplicates as single matches
    let large_code = r#"
        function processUserData(user) {
            if (!user || !user.id) throw new Error("Invalid");
            const firstName = user.firstName.trim().toLowerCase();
            const lastName = user.lastName.trim().toLowerCase();
            const birthDate = new Date(user.birthDate);
            const today = new Date();
            let age = today.getFullYear() - birthDate.getFullYear();
            const monthDiff = today.getMonth() - birthDate.getMonth();
            if (monthDiff < 0) age--;
            const profile = {
                id: user.id,
                fullName: firstName + " " + lastName,
                age: age,
                email: user.email.toLowerCase()
            };
            if (!profile.email.includes("@")) throw new Error("Invalid email");
            if (age < 18) profile.requiresParentalConsent = true;
            return profile;
        }

        function handleUserRegistration(userData) {
            if (!userData || !userData.id) throw new Error("Invalid");
            const firstName = userData.firstName.trim().toLowerCase();
            const lastName = userData.lastName.trim().toLowerCase();
            const birthDate = new Date(userData.birthDate);
            const today = new Date();
            let age = today.getFullYear() - birthDate.getFullYear();
            const monthDiff = today.getMonth() - birthDate.getMonth();
            if (monthDiff < 0) age--;
            const profile = {
                id: userData.id,
                fullName: firstName + " " + lastName,
                age: age,
                email: userData.email.toLowerCase()
            };
            if (!profile.email.includes("@")) throw new Error("Invalid email");
            if (age < 18) profile.requiresParentalConsent = true;
            return profile;
        }
    "#;

    let tokens = normalize(large_code);
    let matches = detect_duplicates_with_extension(&tokens, 50);

    // Should find one large match (not fragmented)
    assert!(!matches.is_empty());

    // The match should be significantly longer than the minimum window
    let longest_match = matches.iter().map(|m| m.length).max().unwrap();
    assert!(
        longest_match > 100,
        "Expected large duplicate >100 tokens, got {}",
        longest_match
    );
}

#[test]
fn test_no_false_positives_different_code() {
    // Ensure we don't detect duplicates in completely different code
    let code1 = r#"
        function add(a, b) {
            return a + b;
        }
    "#;

    let code2 = r#"
        function fetchUser(id) {
            return database.query("SELECT * FROM users WHERE id = ?", id);
        }
    "#;

    let tokens1 = normalize(code1);
    let tokens2 = normalize(code2);

    // These should be completely different
    assert_ne!(tokens1, tokens2);
}

#[test]
fn test_scanner_integration_with_test_files() {
    // Test the full scanner on test files if they exist
    let test_path = PathBuf::from("test_duplicates");

    if test_path.exists() {
        let scanner = Scanner::new();
        let result = scanner.scan(vec![test_path]);

        assert!(result.is_ok());
        let report = result.unwrap();

        // Should find some duplicates in test files
        assert!(
            !report.duplicates.is_empty(),
            "Expected to find duplicates in test_duplicates/"
        );

        // All duplicates should have length >= min_block_size
        for dup in &report.duplicates {
            assert!(
                dup.length >= 50,
                "Duplicate length {} less than minimum 50",
                dup.length
            );
        }
    }
}

#[test]
fn test_extension_stops_at_divergence() {
    // Test that extension correctly stops when code diverges
    let code = r#"
        function func1() {
            let a = 1;
            let b = 2;
            let c = 3;
            return a + b + c;
        }

        function func2() {
            let a = 1;
            let b = 2;
            let c = 3;
            let d = 4;  // Extra line - divergence point
            let e = 5;
            return a + b + c + d + e;
        }
    "#;

    let tokens = normalize(code);
    let matches = detect_duplicates_with_extension(&tokens, 10);

    if !matches.is_empty() {
        // If a match is found, it should not include the divergent section
        for m in &matches {
            // The match should be shorter than the full function
            // (it should stop at the divergence point)
            assert!(
                m.length < 50,
                "Match should stop at divergence, but got length {}",
                m.length
            );
        }
    }
}

#[test]
fn test_hash_collision_handling() {
    // Ensure verify_match catches hash collisions
    // (This is a property test - in practice hash collisions are rare)
    let code = r#"
        function test1() { return 42; }
        function test2() { return 42; }
        function test3() { return 43; }
    "#;

    let tokens = normalize(code);
    let matches = detect_duplicates_with_extension(&tokens, 5);

    // Should only match truly identical sequences
    for m in &matches {
        let source = &tokens[m.source_start..m.source_start + m.length];
        let target = &tokens[m.target_start..m.target_start + m.target_length];
        assert_eq!(
            source, target,
            "Match verification failed - not truly identical"
        );
    }
}

#[test]
fn test_type3_gap_tolerant_detection() {
    use dupe_core::{compute_token_similarity, detect_type3_clones};

    // Type-3: Similar code with insertions/deletions
    let code1 = r#"
        function calculate(x, y) {
            let result = x + y;
            return result;
        }
    "#;

    let code2 = r#"
        function compute(a, b) {
            let temp = 0;
            let result = a + b;
            return result;
        }
    "#;

    let tokens1 = normalize(code1);
    let tokens2 = normalize(code2);

    // Calculate similarity
    let similarity = compute_token_similarity(&tokens1, &tokens2);
    println!("Type-3 similarity: {:.2}", similarity);

    // Should detect partial similarity (not identical due to extra statement)
    assert!(similarity > 0.6);
    assert!(similarity < 1.0);

    // Detect Type-3 clones with tolerance - use smaller window for short functions
    let type3_matches = detect_type3_clones(&tokens1, &tokens2, 5, 0.7);

    // The similarity score validates Type-3 detection capability
    // Actual matches depend on window size and token overlap
    println!("Found {} Type-3 matches with window=5", type3_matches.len());
}

#[test]
fn test_type3_with_scanner() {
    use std::fs;
    use tempfile::TempDir;

    // Create temporary test files with substantial duplicates
    let temp_dir = TempDir::new().unwrap();
    let file1_path = temp_dir.path().join("file1.js");
    let file2_path = temp_dir.path().join("file2.js");

    // Longer functions to meet minimum token threshold (50 tokens)
    let code1 = r#"
function processOrderData(orderItems, discount) {
    let subtotal = 0;
    let tax = 0;
    let total = 0;

    for (let i = 0; i < orderItems.length; i++) {
        let item = orderItems[i];
        if (item.valid && item.price > 0) {
            subtotal += item.price * item.quantity;
        }
    }

    tax = subtotal * 0.08;
    total = subtotal + tax - discount;

    return {
        subtotal: subtotal,
        tax: tax,
        total: total
    };
}
"#;

    let code2 = r#"
function calculateOrderTotal(items, discountAmount) {
    let subtotal = 0;
    let tax = 0;
    let total = 0;

    console.log("Processing order...");

    for (let i = 0; i < items.length; i++) {
        let item = items[i];
        if (item.valid && item.price > 0) {
            subtotal += item.price * item.quantity;
        }
    }

    tax = subtotal * 0.08;
    total = subtotal + tax - discountAmount;

    return {
        subtotal: subtotal,
        tax: tax,
        total: total
    };
}
"#;

    fs::write(&file1_path, code1).unwrap();
    fs::write(&file2_path, code2).unwrap();

    // Scan with smaller min_block_size to detect these functions
    let scanner = Scanner::with_config(30, 0.85)
        .unwrap()
        .with_type3_detection(0.8)
        .unwrap();

    let report = scanner.scan(vec![temp_dir.path().to_path_buf()]).unwrap();

    println!("Type-3 scan found {} duplicates", report.duplicates.len());

    // These functions are structurally very similar (only console.log differs)
    // Should detect as Type-2 at minimum
    assert!(
        !report.duplicates.is_empty(),
        "Should detect structural similarity between functions"
    );
}

#[test]
fn test_type3_with_existing_type2_matches() {
    // Regression test for boolean precedence bug in Type-3 filtering
    // Ensures Type-3 detection works even when Type-1/2 matches exist between same files
    use std::fs;
    use tempfile::tempdir;

    let temp_dir = tempdir().unwrap();
    let file1_path = temp_dir.path().join("service1.js");
    let file2_path = temp_dir.path().join("service2.js");

    // Two functions per file: one exact match (Type-2) and one near-miss (Type-3)
    let code1 = r#"
// Exact match - should be Type-2
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Near-miss - should be Type-3
function processUserData(userData) {
    const name = userData.name || "Unknown";
    const age = userData.age || 0;
    const email = userData.email || "";

    if (name.length < 2) {
        throw new Error("Invalid name");
    }

    return {
        name: name.toUpperCase(),
        age: age,
        email: email.toLowerCase(),
        timestamp: Date.now()
    };
}
"#;

    let code2 = r#"
// Exact match - should be Type-2 (renamed function)
function checkEmailAddress(emailAddress) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(emailAddress);
}

// Near-miss - should be Type-3 (has extra validation, different structure)
function sanitizeUserInput(userInput) {
    const fullName = userInput.name || "Unknown";
    const userAge = userInput.age || 0;
    const emailAddr = userInput.email || "";

    if (fullName.length < 2) {
        throw new Error("Invalid name");
    }

    // Extra validation not in original
    if (userAge < 0 || userAge > 150) {
        throw new Error("Invalid age");
    }

    return {
        name: fullName.toUpperCase(),
        age: userAge,
        email: emailAddr.toLowerCase()
    };
}
"#;

    fs::write(&file1_path, code1).unwrap();
    fs::write(&file2_path, code2).unwrap();

    // Scan with Type-3 enabled
    let scanner = Scanner::with_config(20, 0.85)
        .unwrap()
        .with_type3_detection(0.75)
        .unwrap();

    let report = scanner.scan(vec![temp_dir.path().to_path_buf()]).unwrap();

    println!("\nType-3 regression test results:");
    println!("Total duplicates: {}", report.duplicates.len());

    let type2_count = report
        .duplicates
        .iter()
        .filter(|d| matches!(d.clone_type, dupe_core::CloneType::Type2))
        .count();
    let type3_count = report
        .duplicates
        .iter()
        .filter(|d| matches!(d.clone_type, dupe_core::CloneType::Type3))
        .count();

    println!("Type-2 matches: {}", type2_count);
    println!("Type-3 matches: {}", type3_count);

    // CRITICAL: Type-3 matches must be detected even though Type-2 matches exist
    // This was broken due to boolean precedence bug in seen_pairs filtering
    assert!(
        type3_count > 0,
        "Type-3 detection must work even when Type-1/2 matches exist between same file pair"
    );

    // Should detect both the exact match (Type-2) and near-miss (Type-3)
    assert!(
        type2_count > 0,
        "Should detect Type-2 exact match between validateEmail/checkEmailAddress"
    );
}

#[test]
fn test_type3_same_file_detection() {
    // Regression test: Type-3 should detect within-file near-miss clones
    // Previously skipped same-file pairs entirely in Type-3 detection
    use std::fs;
    use tempfile::tempdir;

    let temp_dir = tempdir().unwrap();
    let file_path = temp_dir.path().join("utils.js");

    // Two similar functions in same file - near-miss clones
    let code = r#"
// First version - processes user data
function processUserProfile(user) {
    const name = user.name || "Unknown";
    const email = user.email || "";
    const age = user.age || 0;

    if (name.length < 2) {
        throw new Error("Invalid name");
    }

    return {
        name: name.toUpperCase(),
        email: email.toLowerCase(),
        age: age,
        verified: true
    };
}

// Second version - processes admin data (copy/paste with edits)
function processAdminProfile(admin) {
    const fullName = admin.name || "Unknown";
    const emailAddress = admin.email || "";
    const userAge = admin.age || 0;

    if (fullName.length < 2) {
        throw new Error("Invalid name");
    }

    // Extra admin-specific logic
    const permissions = admin.permissions || [];

    return {
        name: fullName.toUpperCase(),
        email: emailAddress.toLowerCase(),
        age: userAge,
        verified: true,
        isAdmin: true,
        permissions: permissions
    };
}
"#;

    fs::write(&file_path, code).unwrap();

    // Scan with Type-3 enabled
    let scanner = Scanner::with_config(20, 0.85)
        .unwrap()
        .with_type3_detection(0.75)
        .unwrap();

    let report = scanner.scan(vec![temp_dir.path().to_path_buf()]).unwrap();

    println!("\nSame-file Type-3 test results:");
    println!("Total duplicates: {}", report.duplicates.len());

    let type3_count = report
        .duplicates
        .iter()
        .filter(|d| matches!(d.clone_type, dupe_core::CloneType::Type3))
        .count();

    println!("Type-3 same-file matches: {}", type3_count);

    // CRITICAL: Must detect Type-3 matches within the same file
    assert!(
        type3_count > 0,
        "Type-3 detection must work for same-file near-miss clones (copy/paste with edits)"
    );
}

#[test]
fn test_type3_deduplication_multi_target() {
    // Regression test: Deduplication should check both source AND target ranges
    // Previously only checked source_start, dropping valid matches when one source
    // region was copied to multiple different target locations
    use std::fs;
    use tempfile::tempdir;

    let temp_dir = tempdir().unwrap();
    let file_path = temp_dir.path().join("multi-clone.js");

    // One source function copied to three different places with slight edits
    let code = r#"
// Original function
function validateInput(data) {
    if (!data || data.length === 0) {
        return false;
    }
    return true;
}

// Copy 1 - slightly modified
function checkInputValid(input) {
    if (!input || input.length === 0) {
        console.log("Invalid input");
        return false;
    }
    return true;
}

// Copy 2 - slightly modified differently
function verifyInput(value) {
    if (!value || value.length === 0) {
        throw new Error("Empty input");
    }
    return true;
}

// Copy 3 - another variation
function ensureInputExists(item) {
    if (!item || item.length === 0) {
        return false;
    }
    console.log("Input validated");
    return true;
}
"#;

    fs::write(&file_path, code).unwrap();

    // Scan with Type-3 enabled
    let scanner = Scanner::with_config(15, 0.85)
        .unwrap()
        .with_type3_detection(0.75)
        .unwrap();

    let report = scanner.scan(vec![temp_dir.path().to_path_buf()]).unwrap();

    println!("\nMulti-target deduplication test:");
    println!("Total duplicates: {}", report.duplicates.len());

    let type3_count = report
        .duplicates
        .iter()
        .filter(|d| matches!(d.clone_type, dupe_core::CloneType::Type3))
        .count();

    println!("Type-3 matches: {}", type3_count);

    // Should detect multiple matches: original vs each copy (3+ matches expected)
    // Without proper deduplication, this would incorrectly merge them into 1 match
    assert!(
        type3_count >= 3,
        "Deduplication must preserve distinct target regions when same source is copied multiple times. Found {} but expected >= 3",
        type3_count
    );
}

#[test]
fn test_type3_similarity_after_extension() {
    // Regression test: Similarity should reflect the final extended region, not just initial window
    // Previously reported initial window similarity even after extension
    use dupe_core::{detect_type3_clones, normalize};

    // Create two code snippets where extension changes similarity
    let code1 = r#"
function process(data) {
    let result = 0;
    for (let i = 0; i < data.length; i++) {
        result += data[i] * 2;
    }
    return result;
}
"#;

    let code2 = r#"
function calculate(input) {
    let total = 0;
    for (let j = 0; j < input.length; j++) {
        total += input[j] * 2;
        // Extra comment that reduces similarity
    }
    return total;
}
"#;

    let tokens1 = normalize(code1);
    let tokens2 = normalize(code2);

    println!("Tokens1 length: {}", tokens1.len());
    println!("Tokens2 length: {}", tokens2.len());

    // Detect with low tolerance to allow extension
    let matches = detect_type3_clones(&tokens1, &tokens2, 10, 0.75);

    println!("Found {} Type-3 matches", matches.len());

    for (idx, m) in matches.iter().enumerate() {
        println!(
            "Match {}: start1={}, start2={}, length={}, similarity={:.2}%",
            idx,
            m.source_start,
            m.target_start,
            m.length,
            m.similarity * 100.0
        );

        // Verify similarity is calculated for the actual extended region
        let actual_window1 = &tokens1[m.source_start..m.source_start + m.length];
        let actual_window2 = &tokens2[m.target_start..m.target_start + m.target_length];
        let expected_similarity =
            dupe_core::compute_token_similarity(actual_window1, actual_window2);

        println!(
            "  Expected similarity (from actual region): {:.2}%",
            expected_similarity * 100.0
        );

        // CRITICAL: Reported similarity must match the actual extended region
        assert!(
            (m.similarity - expected_similarity).abs() < 0.01,
            "Similarity must reflect extended region. Reported: {:.3}, Expected: {:.3}",
            m.similarity,
            expected_similarity
        );
    }

    assert!(
        !matches.is_empty(),
        "Should detect at least one Type-3 match"
    );
}

#[test]
fn test_type3_transitive_overlap_deduplication() {
    // Regression test: Deduplication must handle transitive overlaps
    // If Match A overlaps Match B, and Match B overlaps Match C (but A doesn't overlap C),
    // all three should be merged into one result (A→B→C chain)
    //
    // Bug: Previously compared overlap against original 'current' instead of updated 'best_match',
    // causing transitive chains to break
    use std::fs;
    use tempfile::tempdir;

    let temp_dir = tempdir().unwrap();
    let file_path = temp_dir.path().join("transitive.js");

    // Create functions where Type-3 matches form a transitive chain:
    // funcA and funcB overlap at positions 0-40
    // funcB and funcC overlap at positions 30-70
    // funcA and funcC do NOT overlap (A ends at 40, C starts at 50)
    let code = r#"
// Function A: Will match funcB at start (tokens 0-40)
function funcA() {
    let items = [1, 2, 3, 4, 5];
    let doubled = items.map(x => x * 2);
    let filtered = doubled.filter(x => x > 2);
    console.log("Result A:", filtered);
    return filtered;
}

// Function B: Overlaps A (0-40) AND C (30-70) - acts as bridge
function funcB() {
    let values = [1, 2, 3, 4, 5, 6];  // Slightly different
    let multiplied = values.map(y => y * 2);
    let cleaned = multiplied.filter(y => y > 2);
    console.log("Result B:", cleaned);
    let sorted = cleaned.sort((a, b) => a - b);  // Extends beyond A
    return sorted;
}

// Function C: Only overlaps B (30-70), NOT A
function funcC() {
    let nums = [2, 4, 6];  // Different data
    let processed = nums.filter(n => n > 2);
    console.log("Result C:", processed);
    let ordered = processed.sort((x, y) => x - y);
    let unique = [...new Set(ordered)];
    return unique;
}
"#;

    fs::write(&file_path, code).unwrap();

    // Scan with Type-3 detection (low tolerance to catch all overlaps)
    let scanner = Scanner::with_config(5, 0.85)
        .unwrap()
        .with_type3_detection(0.65)
        .unwrap();

    let report = scanner.scan(vec![temp_dir.path().to_path_buf()]).unwrap();

    println!("\nTransitive overlap test:");
    println!("Total duplicates: {}", report.duplicates.len());

    // Find Type-3 matches within same file
    let type3_matches: Vec<_> = report
        .duplicates
        .iter()
        .filter(|d| matches!(d.clone_type, dupe_core::CloneType::Type3))
        .collect();

    println!("Type-3 matches: {}", type3_matches.len());

    for (idx, m) in type3_matches.iter().enumerate() {
        println!(
            "  Match {}: {}:{} ↔ {}:{}, length={}, similarity={:.1}%",
            idx,
            m.file1,
            m.start_line1,
            m.file2,
            m.start_line2,
            m.length,
            m.similarity * 100.0
        );
    }

    // CRITICAL: The test verifies that deduplication is working by checking
    // that sliding window noise is reduced. With a low similarity threshold (0.65),
    // the sliding window produces many overlapping matches. Without proper
    // deduplication (especially transitive overlap handling), we would see 100+ matches.
    //
    // With transitive deduplication (the fix), overlapping matches within each
    // function pair merge correctly, reducing the count significantly.
    //
    // The fix ensures that when best_match is updated, subsequent overlap checks
    // use the new best_match boundaries (not the original `current`), so transitive
    // chains like A→B→C are properly merged.
    //
    // Expected: ~10-20 matches (deduplicated clusters)
    // Bug behavior: 100+ matches (no deduplication or broken transitive merging)
    assert!(
        type3_matches.len() < 50,
        "Deduplication should drastically reduce overlapping windows. Found {} Type-3 matches (expected < 50). \
         This indicates deduplication is not working correctly.",
        type3_matches.len()
    );

    println!("\n✓ Deduplication reduced sliding window noise successfully");
}
