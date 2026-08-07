//! Criterion harness for the core reducer. Real reducer benchmarks arrive with
//! CV-003; this keeps `just bench` (validation ladder L3) wired from day one.

use criterion::{Criterion, criterion_group, criterion_main};

fn version_lookup(c: &mut Criterion) {
    c.bench_function("cv_core::VERSION", |b| {
        b.iter(|| std::hint::black_box(cv_core::VERSION));
    });
}

criterion_group!(benches, version_lookup);
criterion_main!(benches);
