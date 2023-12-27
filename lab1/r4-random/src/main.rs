/**** Architettura del programma ****
 * Il lavoro viene eseguito in parallelo da 20 thread.
 * Ogni volta che un thread completa una milestone,
 *   invia i risultati attuali al `main()`.
 * Quando il programma principale
*/

/*** Costanti per la compilazione ***/
// Parametri della simulazione
const N_THREADS:    u8  = 20;        // Numero di thread
const N_MILESTONES: u32 = 10_000;    // Numero di milestone
const N_THROWS:     u32 = 5_000_000; // Numero di lanci per milestone
const N_ROLLS:      u8  = 6;         // Numero di dadi da lanciare
// Altre costanti
const N_BINS: usize = (N_ROLLS + 1) as usize;
const N_COUNT_TOTAL: u128 = (N_MILESTONES as u128) * (N_THREADS as u128);

/*** Importazioni ***/
use std::{sync::mpsc::{self, Sender}, thread, io::{self, Write}};
use rand::prelude::Distribution;


/*** Lavoro di ogni thread ***/
fn work(tx: Sender<[u128; N_BINS]>) {
    let mut rng = rand::thread_rng();
    let die = rand::distributions::Uniform::from(1..7u8);
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


/*** Utility per l'output ***/

fn print_info() {
    // Stampa a schermo la configurazione iniziale
    println!("#dadi:   {N_ROLLS}");
    println!("#lanci:  {N_THROWS}");
    println!("#volte:  {N_MILESTONES}");
    println!("#thread: {N_THREADS}");
    let total: u128 = (N_THROWS as u128)*N_COUNT_TOTAL;
    println!("#totale: {total}");
}

fn print_bins(count: u128, bins: [u128; N_BINS]) {
    // Stampa a schermo il progresso attuale e i conteggi dei bin
    let percent: u128 = (100*count)/N_COUNT_TOTAL;
    print!("[{count}/{N_COUNT_TOTAL}|{percent}%]");
    for i in 0..N_BINS {
        let bin = bins[i];
        print!("\t{bin}");
    }
    print!("\n");
    io::stdout().flush().unwrap();
}


/*** Programma principale ***/
fn main() {
    print_info();
    // Crea i thread
    let (tx, rx) = mpsc::channel::<[u128;N_BINS]>();
    for _i in 0..N_THREADS {
        let txi = tx.clone();
        thread::spawn(move ||{ work(txi); });
    }
    // Combina gli output
    let mut count: u128 = 0;
    let mut bins: [u128; N_BINS] = [0; N_BINS];
    for bin in rx {
        for i in 0..N_BINS {
            bins[i] += bin[i];
        }
        count += 1;  // Un altro thread ha finito!
        if (count % (N_THREADS as u128)) == 0 {
            print_bins(count, bins);
        }
        if count == N_COUNT_TOTAL {
            break;
        }
    }
}
