# arraystream Roadmap

## Current Status (v0.1.0)

### ✅ Completed
- [x] Project structure and build system (maturin, PyO3)
- [x] Core Python implementations for all planned functions
- [x] Rust module structure and compilation setup
- [x] Comprehensive test suite (88 tests, all passing)
- [x] Python fallback implementations working correctly
- [x] Support for all 10 typecodes: `b`, `B`, `h`, `H`, `i`, `I`, `l`, `L`, `f`, `d`
- [x] Structural transforms: `chunked`, `windowed`, `take`, `drop`, `interleave`, `repeat_each`
- [x] Numeric operations: `scan`, `diff`, `pairwise`, `clip` (Python implementations)
- [x] Boolean operations: `where`, `argwhere`, `mask`
- [x] Grouping operations: `run_length_encode`, `groupby_runs` (Python implementations)

### 🐛 Known Issues
- [ ] Rust implementations have runtime error: `TypeError: 'str' object cannot be interpreted as an integer`
- [ ] Rust code compiles but fails when extracting array elements from Python lists
- [ ] Currently using Python fallbacks for all Rust-backed functions

---

## Short-Term Goals (v0.2.0)

### Priority 1: Fix Rust Implementation
- [ ] **Debug and fix Rust array extraction**
  - [ ] Investigate PyO3 API for extracting integers from Python lists
  - [ ] Consider using buffer protocol directly instead of `tolist()`
  - [ ] Add comprehensive error handling and debugging
  - [ ] Test with different PyO3 versions if needed
  - [ ] Verify all 10 typecodes work correctly in Rust

- [ ] **Enable Rust implementations**
  - [ ] Re-enable Rust code paths in `numeric.py` and `grouping.py`
  - [ ] Verify performance improvements
  - [ ] Ensure all tests still pass with Rust implementations

### Priority 2: Testing & Documentation
- [ ] Add performance benchmarks comparing Python vs Rust
- [ ] Add integration tests with `arrayops` (when available)
- [ ] Improve error messages and type checking
- [ ] Add usage examples to README

---

## Medium-Term Goals (v0.3.0 - v0.5.0)

### Performance Optimizations
- [ ] **Zero-copy views where possible**
  - [ ] Implement view-based operations for `take`, `drop`, `windowed`
  - [ ] Use memory views for structural transforms that don't modify data
  - [ ] Document allocation behavior for each function

- [ ] **Rust optimizations**
  - [ ] SIMD optimizations for numeric operations (scan, diff, clip)
  - [ ] Parallel processing for large arrays where beneficial
  - [ ] Optimize grouping operations (RLE, groupby_runs)

### Additional Features
- [ ] **More scan operations**
  - [ ] `scan` with `"product"`, `"min"`, `"max"` operations
  - [ ] Custom reducer functions (if feasible)

- [ ] **Additional structural transforms**
  - [ ] `rotate`, `reverse`, `shuffle`
  - [ ] `split_at`, `partition`
  - [ ] `zip`, `unzip` for multiple arrays

- [ ] **Advanced grouping**
  - [ ] `groupby` with custom key functions
  - [ ] `chunk_by` (group by predicate)
  - [ ] `segment` (split at boundaries)

- [ ] **Indexing and selection**
  - [ ] `gather` (select by indices)
  - [ ] `scatter` (assign by indices)
  - [ ] `take_while`, `drop_while`

### Integration
- [ ] **arrayops integration**
  - [ ] Use `arrayops.sum` when available for scan operations
  - [ ] Leverage `arrayops` for other numeric kernels
  - [ ] Document complementary relationship

- [ ] **Type system improvements**
  - [ ] Better type hints for all functions
  - [ ] Support for `typing.Protocol` for buffer-like objects
  - [ ] Generic type preservation

---

## Long-Term Goals (v0.6.0+)

### API Enhancements
- [ ] **Iterator/streaming API**
  - [ ] Lazy evaluation for chained operations
  - [ ] Iterator-based implementations for memory efficiency
  - [ ] Streaming operations for very large arrays

- [ ] **Composition utilities**
  - [ ] Function composition helpers
  - [ ] Pipeline syntax sugar
  - [ ] Operator overloading (if appropriate)

### Ecosystem
- [ ] **NumPy integration** (optional)
  - [ ] Support for `numpy.ndarray` as input (via buffer protocol)
  - [ ] Output to NumPy arrays when requested
  - [ ] Keep zero dependencies on NumPy core

- [ ] **Documentation**
  - [ ] Comprehensive API documentation
  - [ ] Performance guide
  - [ ] Best practices and patterns
  - [ ] Comparison with similar libraries

### Advanced Features
- [ ] **Multi-dimensional support** (if needed)
  - [ ] 2D array operations
  - [ ] Flattening/reshaping utilities

- [ ] **Custom allocators**
  - [ ] Support for custom memory allocators
  - [ ] Memory pool integration

---

## Technical Debt

### Code Quality
- [ ] Remove unused imports and code
- [ ] Add more comprehensive error handling
- [ ] Improve code organization and modularity
- [ ] Add docstrings to all Rust functions

### Testing
- [ ] Add property-based tests (using Hypothesis)
- [ ] Add fuzzing for edge cases
- [ ] Performance regression tests
- [ ] Cross-platform testing (Windows, Linux)

### Build & Distribution
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Automated releases
- [ ] Pre-built wheels for common platforms
- [ ] Documentation generation

---

## Research & Exploration

### Potential Optimizations
- [ ] Investigate `ndarray` crate for Rust-side array handling
- [ ] Explore `rayon` for parallel processing
- [ ] Consider `unsafe` Rust for performance-critical paths (with careful review)
- [ ] Benchmark against NumPy operations (where applicable)

### API Design
- [ ] Gather user feedback on API ergonomics
- [ ] Consider adding builder patterns for complex operations
- [ ] Evaluate request for additional operations

---

## Version History

### v0.1.0 (Current)
- Initial release with Python implementations
- Rust module structure in place
- Comprehensive test suite
- All core operations implemented

### v0.2.0 (Planned)
- Fixed Rust implementations
- Performance benchmarks
- Improved documentation

### v0.3.0 (Planned)
- Zero-copy optimizations
- Additional scan operations
- More structural transforms

---

## Contributing

We welcome contributions! Areas where help is especially needed:

1. **Rust debugging**: Help fix the array extraction issue
2. **Performance**: Optimize existing operations
3. **Testing**: Add more comprehensive test coverage
4. **Documentation**: Improve docs and examples
5. **Features**: Implement new operations from the roadmap

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines (to be created).

---

## Notes

- This roadmap is a living document and may change based on user feedback and priorities
- Dates are intentionally omitted to focus on feature completeness over deadlines
- Performance is a key goal, but correctness and API design come first
- The package aims to stay small, focused, and dependency-light

