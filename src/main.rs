/*** Constants ***/
const N_THREADS: usize = 50;
const N_THROWS: u64 = 20_000_000_000;
const N_ROLLS: u8 = 5;
const N_BINS: usize = (N_ROLLS + 1) as usize;

/*** Imports ***/
use std::{sync::mpsc::{self, Sender}, thread};
use rand::prelude::Distribution;


fn work(tx: Sender<[u128; N_BINS]>) {
    /*** Setup ***/
    println!("work: start");
    let mut rng = rand::thread_rng();
    let die = rand::distributions::Uniform::from(1..7u8);
    /*** Main program ***/
    let mut counter: u8;
    let mut bins: [u128; N_BINS] = [0; N_BINS];
    for _i in 0..N_THROWS {
        counter = 0;
        for _m in 0..N_ROLLS {
            // Roll a die
            if die.sample(&mut rng) == 1 {
                counter += 1;   // Success!
            }
        }
        bins[counter as usize] += 1;
    }
    println!("work: done");
    tx.send(bins).unwrap();
}


fn main() {
    /*** Setup ***/
    println!("[i] Lancio {N_ROLLS} dadi {N_THROWS} volte su ognuno dei {N_THREADS} thread.");
    let (tx, rx) = mpsc::channel::<[u128;N_BINS]>();
    /*** Threads ***/
    for _i in 0..N_THREADS {
        let txi = tx.clone();
        thread::spawn(move ||{ work(txi); });
    }
    /*** Combine all outputs ***/
    let mut answers: usize = 0;
    let mut bins: [u128; N_BINS] = [0; N_BINS];
    for bin in rx {
        for i in 0..N_BINS {
            bins[i] += bin[i];
        }
        answers += 1;
        if answers >= N_THREADS {
            break;
        }
    }
    // /*** Join all threads ***/
    // for thread in threads {
    //     thread.join().unwrap();
    // }
    /*** Output ***/
    for m in 0..N_BINS {
        let bin = bins[m];
        println!("#{m}: {bin}");
    }
}
