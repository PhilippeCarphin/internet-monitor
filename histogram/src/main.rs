use chrono;
use std::env::args;
use std::error::Error;
use std::io::BufRead;

/*
 * The script pings.sh which sends One ping to google.com every ~25 seconds and
 * outputs the success or failure of this ping.
 *
 * This program will create a histogram with hours on the X axis and on the Y
 * axix how much time the internet was out during this hour.
 *
 */

#[derive(Debug)]
#[allow(dead_code)]
struct Ping {
    success: bool,
    millis: f32,
    date: chrono::NaiveDateTime,
}

fn main() -> Result<(), Box<dyn Error>> {
    let args_vec: Vec<_> = args().collect();
    let filename = args_vec
        .get(1)
        .ok_or("One filename argument must be provided")?;
    let file = std::fs::File::open(filename)?;
    let buf = std::io::BufReader::new(file);
    for (i, l) in buf.lines().enumerate() {
        if let Ok(l) = l {
            let ping_result = line_to_ping_result(&l)?;
        }
        if i == 8 {
            return Ok(());
        }
    }
    Ok(())
}

/*
 * Ping result as produced by pings.sh are of the form
 *
 *     "Internet working at 2023-04-13 18:23:00 (time=12.987)"
 * or
 *     "Internet down at 2023-04-13 18:23:00"
 *
 * it's like that because I wasn't expecting to do anything more with the data
 * otherwise it would have been more structured but hey, it's making me work
 * on my rust skills.
 */
fn line_to_ping_result(line: &str) -> Result<Ping, Box<dyn Error>> {
    let words: Vec<_> = line.split(" ").collect();
    let success = match *(words.get(1).ok_or("Invalid ping result line: no word[1]")?) {
        "down" => false,
        "working" => true,
        _ => {
            return Err("Word 2 is not 'down' or 'working'".into());
        }
    };
    let date_time_str = format!(
        "{} {}",
        words.get(3).ok_or("Missing word[3]")?,
        words.get(4).ok_or("Missing word[4]")?
    );
    let date = chrono::NaiveDateTime::parse_from_str(&date_time_str, "%Y-%m-%d %H:%M:%S")?;
    let millis: f32 = if success {
        let time_str = words.get(5).ok_or("Missing word[5] for successful ping")?;
        let millis_str: &str = &time_str["(time=".len()..time_str.len() - 1];
        millis_str.parse()?
    } else {
        0.0
    };
    let p = Ping {
        success,
        millis,
        date,
    };
    Ok(p)
}
