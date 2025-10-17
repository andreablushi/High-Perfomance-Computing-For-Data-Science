#include <stdio.h>
#include <string.h>   /* For strlen */
#include <mpi.h>      /* For MPI functions */

#define ITERATION_LIMIT 10
const int MAX_STRING = 100;

/*
    Task:
    CLOSED RING
    Write a program that takes data from process zero and sends it to all of
    the other processes by sending it in a ring. That is, process i should
    receive the data and send it to process i+1, until the last process is
    reached, and finally it goes back to process 0.
    Then define the PBS script and command to submit your job.
*/

int main(void) {
    int comm_sz;    /* Number of processes */
    int my_rank;    /* My process rank     */
    int count = 0;  /* Iteration counter   */

    MPI_Init(NULL, NULL);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_sz);
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

    // Process 0 starts the secret message
    if (my_rank == 0) {
        char* msg = "Secret message";
        printf("I'm process %d and I'm writing a message to process %d!\n",
               my_rank, (my_rank + 1) % comm_sz);
        MPI_Send(msg, strlen(msg) + 1, MPI_CHAR,
                 (my_rank + 1) % comm_sz, 0, MPI_COMM_WORLD);
    }

    // Loop for ITERATION_LIMIT passes of the message around the ring
    while (count < ITERATION_LIMIT) {
        char msg[MAX_STRING];
        int next_rank = (my_rank + 1) % comm_sz;          // Next process in the ring
        int prev_rank = (my_rank - 1 + comm_sz) % comm_sz; // Previous process in the ring
        // Receive the message from the previous process
        MPI_Recv(msg, MAX_STRING, MPI_CHAR, prev_rank, 0,
                 MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("I'm process %d, received from process %d, sending to process %d\n",
               my_rank, prev_rank, next_rank);
        // Send the message to the next process
        MPI_Send(msg, strlen(msg) + 1, MPI_CHAR, next_rank, 0, MPI_COMM_WORLD);
        // Counting one iteration
        if(my_rank == 0){
            count++;
        }
    }

    MPI_Finalize();
    return 0;
} /* main */
