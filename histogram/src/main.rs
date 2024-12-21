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
 */

#[derive(Debug, Clone)]
#[allow(dead_code)]
struct Ping {
    success: bool,
    millis: f32,
    date: chrono::NaiveDateTime,
}

#[derive(Debug)]
#[allow(dead_code)]
struct HistogramBar {
    date: chrono::NaiveDateTime,
    time_offline: std::time::Duration,
}

#[derive(Debug)]
#[allow(dead_code)]
struct Histogram {
    bars: Vec<HistogramBar>,
    bar: Option<HistogramBar>,
    last_success: Option<Ping>,
    last_fail: Option<Ping>,
    previous_ping: Option<Ping>,
}

#[allow(dead_code)]
impl Histogram {
    fn ingest_ping(&mut self, ping: &Ping) -> Result<(), Box<dyn Error>> {
        println!("{:?}", ping);
        if self.bar.is_none(){
            // Create new current bar
            // with the hour of the current ping being ingested
            // This should only happen at the first ping ingested ever
        }

        if self.previous_ping.is_none() {
            self.previous_ping = Some(ping.clone());
            return Ok(());
        }

        if true /* current ping is in a different hour of than the bar */ {
            // Move bar into the vector
            if let Some(b) = self.bar.take() {
                self.bars.push(b);
                // self.bar = new bar with the current ping's hour;
            }
        }

        let previous_ping = self.previous_ping.clone().unwrap();

        if previous_ping.success && ping.success {
            return Ok(());
        }

        if !previous_ping.success && !ping.success {
            // fail -> fail
            // Add time difference between both pings to offline time of
            // current bar
        }

        if !previous_ping.success && ping.success {
            // fail -> success
            // Add time difference between both pings to offline time of
            // current bar
        }

        if previous_ping.success && !ping.success {
            // success -> fail
            // Don't add anything, this ping marks the start of a failure
        }

        /*
         * The above thing took me two seconds to come up with and the code
         * to complete will not take long, but it is imprecise.
         * - If the previous ping is in a different hour than the current One
         *   then some time may be miscounted.  Because pings occur every ~25
         *   seconds, that means worst case ~25 seconds off per hour which is
         *   not bad.
         * - Summing up times between successive pings is less precise than
         *   taking the difference between the first and last of a series of
         *   consecutive failed pings.  The imprecision is really not that much
         * The real problem is that it just feels less elegant than if we did
         * take the time difference between the first and last pings of a series
         * of consecutive pings.  Something more like
         */

        match (ping.success, &self.last_fail) {
            (false, None) => {
                self.last_fail = Some(ping.clone());
            },
            (true, Some(_lp)) => {
                // We just ended a streak of failures do some stuff
                // There are multiple cases
                // - The streak is wholly within a bar
                // - The streak covers part of the previous bar and part of the
                //   current one
                // - The streak covers a whole bar. I.e. last_fail is more than
                //   one bar (hour) away from the current ping.
                // This approach is less compatible with the the current bar
                // that we push into the vector when we move to the next hour
                // and may require something like an ordered hashmap of bars.
            },
            (true, None) => {
                // Continuing a streak of successes
                // Do nothing
            },
            (false, Some(_lp)) => {
                // Continuing a streak of failures
            }
        }
        Ok(())
    }
}

fn main() -> Result<(), Box<dyn Error>> {
    let args_vec: Vec<_> = args().collect();
    let filename = args_vec
        .get(1)
        .ok_or("One filename argument must be provided")?;
    let file = std::fs::File::open(filename)?;
    let buf = std::io::BufReader::new(file);
    let mut histogram = Histogram {
        bars: vec![],
        bar: None,
        last_success: None,
        last_fail: None,
        previous_ping: None,
    };
    for (i, l) in buf.lines().enumerate() {
        if let Ok(l) = l {
            let ping_result = line_to_ping_result(&l)?;
            histogram.ingest_ping(&ping_result)?;
        }
        if i == 8 {
            break;
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
