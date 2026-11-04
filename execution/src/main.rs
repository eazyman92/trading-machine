//! No network client or broker submission path. Fixture policy only.
use serde::Deserialize;
use std::io::{self, Read};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Intent {
    schema_version: u64, environment: String, symbol: String, side: String,
    quantity_units: u64, entry_ticks: u64, stop_ticks: u64, target_ticks: u64,
    quote_at_ms: u64, expires_at_ms: u64,
}
fn valid(o: &Intent, now: u64) -> bool {
    let numbers = [o.schema_version, o.quantity_units, o.entry_ticks, o.stop_ticks,
                   o.target_ticks, o.quote_at_ms, o.expires_at_ms];
    if numbers.iter().any(|v| *v == 0 || *v > 1_000_000_000_000_000) { return false; }
    if o.schema_version != 1 || o.environment != "paper" ||
       !["EUR_USD", "GBP_USD"].contains(&o.symbol.as_str()) ||
       !["buy", "sell"].contains(&o.side.as_str()) || o.quantity_units > 10000 { return false; }
    if o.quote_at_ms > now || now-o.quote_at_ms > 2000 ||
       o.expires_at_ms <= now || o.expires_at_ms-now > 60000 { return false; }
    if !(if o.side == "buy" { o.stop_ticks < o.entry_ticks && o.entry_ticks < o.target_ticks }
         else { o.target_ticks < o.entry_ticks && o.entry_ticks < o.stop_ticks }) { return false; }
    let q = o.quantity_units as u128;
    let loss = q*((o.entry_ticks.abs_diff(o.stop_ticks) as u128+1)*10+70);
    let notional = q*o.entry_ticks as u128*10;
    loss <= 25_000_000 && notional <= 10_000_000_000
}
fn main() {
    let result = (|| -> Result<bool, Box<dyn std::error::Error>> {
        let now: u64 = std::env::args().nth(1).ok_or("usage: paper-risk-validator NOW_MS < intent.json")?.parse()?;
        let mut input = String::new(); io::stdin().take(16385).read_to_string(&mut input)?;
        if input.len() > 16384 { return Err("oversized input".into()); }
        let order: Intent = serde_json::from_str(&input)?;
        Ok(valid(&order, now))
    })();
    println!("{{\"accepted_for_paper\":{},\"submitted\":false}}", result.unwrap_or(false));
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn shared_vectors() {
        let cases: serde_json::Value = serde_json::from_str(include_str!("../../contracts/vectors.json")).unwrap();
        for c in cases.as_array().unwrap() {
            let accepted = serde_json::from_value::<Intent>(c["order"].clone()).map(|o| valid(&o, c["now_ms"].as_u64().unwrap())).unwrap_or(false);
            assert_eq!(accepted, c["accepted"].as_bool().unwrap(), "{}", c["name"]);
        }
    }
}
