FROM rust:1.73.0 AS rust-builder

WORKDIR /reddit_app

RUN rustup default stable

#ENV CARGO_HOME=/reddit_app/cargo_home
#ENV RUSTUP_HOME=/reddit_app/rustup_home

RUN cargo install sqlx-cli

RUN mkdir /local_bin/
RUN cp $CARGO_HOME/bin/sqlx /local_bin/

# You don't need this line in the first stage; it'll be used in the next stage
# COPY --from=0 /reddit_app/cargo_home/bin /local_bin

COPY . .

# Second stage: Python setup
FROM python:3.9-slim

# Copy cargo binaries from first stage
#COPY --from=rust-builder /reddit_app/cargo_home/bin /local_bin

WORKDIR /reddit_app

# Set PATH for the binaries from the first stage
ENV PATH="/local_bin:${PATH}"

COPY --from=rust-builder /local_bin/sqlx /usr/local/bin/

COPY wait-for-it.sh /usr/local/bin

COPY . .

COPY entrypoint.sh /reddit_app/
RUN chmod +x /reddit_app/entrypoint.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/reddit_app/entrypoint.sh"]
