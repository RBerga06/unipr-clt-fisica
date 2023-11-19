/**** Architettura del programma ****
 * Il lavoro viene spezzato fra i vari
*/

/* Costanti durante la compilazione */
/// Parametri della simulazione
const N_THREADS:    u8  = 50;        /// Numero di thread
const N_MILESTONES: u32 = 10_000;    /// Numero di
const N_THROWS:     u32 = 2_000_000;
const N_ROLLS:      u8  = 5;
/// Altre costanti
const N_BINS: usize = (N_ROLLS + 1) as usize;
const N_COUNT_TOTAL: u128 = (N_MILESTONES as u128) * (N_THREADS as u128);

/*** Imports ***/
use std::{sync::mpsc::{self, Sender}, thread, io::{self, Write}};
use rand::prelude::Distribution;


fn work(tx: Sender<[u128; N_BINS]>) {
    /*** Setup ***/
    let mut rng = rand::thread_rng();
    let die = rand::distributions::Uniform::from(1..7u8);
    /*** Main program ***/
    let mut counter: u8;
    let mut bins: [u128; N_BINS];
    for _milestone in 0..N_MILESTONES {
        bins = [0; N_BINS];
        for _throw in 0..N_THROWS {
            counter = 0;
            for _roll in 0..N_ROLLS {
                // Roll a die
                if die.sample(&mut rng) == 1 {
                    counter += 1;   // Success!
                }
            }
            bins[counter as usize] += 1;
        }
        tx.send(bins).unwrap();
    }
}


fn print_info() {
    println!("#dadi:   {N_ROLLS}");
    println!("#lanci:  {N_THROWS}");
    println!("#volte:  {N_MILESTONES}");
    println!("#thread: {N_THREADS}");
    let total: u128 = (N_THROWS as u128)*N_COUNT_TOTAL;
    println!("#totale: {total}");
}

fn print_bins(count: u128, bins: [u128; N_BINS]) {
    let percent: u128 = (100*count)/N_COUNT_TOTAL;
    print!("[{count}/{N_COUNT_TOTAL}|{percent}%]");
    for i in 0..N_BINS {
        let bin = bins[i];
        print!("\t{bin}");
    }
    print!("\n");
    io::stdout().flush().unwrap();
}


fn main() {
    print_info();
    /*** Spawn threads ***/
    let (tx, rx) = mpsc::channel::<[u128;N_BINS]>();
    for _i in 0..N_THREADS {
        let txi = tx.clone();
        thread::spawn(move ||{ work(txi); });
    }
    /*** Combine all outputs ***/
    let mut count: u128 = 0;
    let mut bins: [u128; N_BINS] = [0; N_BINS];
    for bin in rx {
        for i in 0..N_BINS {
            bins[i] += bin[i];
        }
        count += 1;  // another thread has finished!
        if (count % (N_THREADS as u128)) == 0 {
            print_bins(count, bins);
        }
        if count == N_COUNT_TOTAL {
            break;
        }
    }
}
