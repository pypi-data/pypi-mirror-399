FROM rust:1.92-slim-bookworm AS builder

COPY . /build

WORKDIR /build

RUN cargo build --release


FROM debian:bookworm-slim

COPY --from=builder /build/target/release/linear_regression /app/linear_regression

RUN chmod +x /app/linear_regression

ENTRYPOINT ["/app/linear_regression"]
