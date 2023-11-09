/*** Constants ***/
const N_THREADS: usize = 50;
const N_MILESTONES: u32 = 10_000;
const N_THROWS: u32 = 2_000_000;
const N_ROLLS: u8 = 5;
const N_BINS: usize = (N_ROLLS + 1) as usize;

/*** Imports ***/
use std::{sync::mpsc::{self, Sender}, thread, io::{self, Write}};
use rand::prelude::Distribution;


fn work(tx: Sender<(u32, [u128; N_BINS])>) {
    /*** Setup ***/
    println!("work: start");
    let mut rng = rand::thread_rng();
    let die = rand::distributions::Uniform::from(1..7u8);
    /*** Main program ***/
    let mut counter: u8;
    let mut bins: [u128; N_BINS];
    for milestone in 0..N_MILESTONES {
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
        tx.send((milestone, bins)).unwrap();
    }
    println!("work: done");
}


fn print_info() {
    println!("#dadi:   {N_ROLLS}");
    println!("#lanci:  {N_THROWS}");
    println!("#volte:  {N_MILESTONES}");
    println!("#thread: {N_THREADS}");
    let total: u128 = (N_ROLLS as u128)*(N_THROWS as u128)*(N_MILESTONES as u128)*(N_THREADS as u128);
    println!("#totale: {total}");
}

fn print_bins(bins: [u128; N_BINS]) {
    print!("->");
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
    let (tx, rx) = mpsc::channel::<(u32, [u128;N_BINS])>();
    for _i in 0..N_THREADS {
        let txi = tx.clone();
        thread::spawn(move ||{ work(txi); });
    }
    /*** Combine all outputs ***/
    let mut done: usize = 0;
    let mut bins: [u128; N_BINS] = [0; N_BINS];
    for (milestone, bin) in rx {
        for i in 0..N_BINS {
            bins[i] += bin[i];
        }
        if milestone == N_MILESTONES - 1 {
            done += 1;  // another thread has finished!
        }
        if done == N_THREADS {
            break;
        }
        print_bins(bins);
    }
}
