FROM rust:1.73.0 AS rust-builder

WORKDIR /chan_app

RUN rustup default stable

RUN cargo install sqlx-cli

RUN mkdir /local_bin/
RUN cp $CARGO_HOME/bin/sqlx /local_bin/

COPY . .

# Second stage: Python setup
FROM python:3.9-slim

WORKDIR /chan_app

ENV PATH="/local_bin:${PATH}"

COPY --from=rust-builder /local_bin/sqlx /usr/local/bin/

COPY wait-for-it.sh /usr/local/bin

COPY . .

COPY entrypoint.sh /chan_app/
RUN chmod +x /chan_app/entrypoint.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/chan_app/entrypoint.sh"]