#include <stdio.h>
#include <string.h>   /* For strlen */
#include <stdlib.h>   // For rand(), srand()
#include <mpi.h>      /* For MPI functions */

const int MAX_STRING = 100;

/*
    BROADCAST TREE-STRUCTURED
    Task:
    Implement a “broadcast” by using send and
    receive
*/

int main(void) {
    int comm_sz;    /* Number of processes */
    int my_rank;    /* My process rank     */

    int msg = 6; // Number to be broadcasted
    MPI_Init(NULL, NULL);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_sz);
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

    // BROADCAST BINARY TREE-STRUCTURED PART
    int step;
    // Iteratively double the step size
    for (step = 1; step < comm_sz; step *= 2) {
        // Just for printing the first message once
        if(my_rank == 0 && step == 1) {
            printf("Process %d broadcasting value %d at step %d\n", my_rank, msg, step);
        }
        // Only processes that have the message && checks if I have to send it to others
        if (my_rank < step && my_rank + step < comm_sz) {
            // rank + step is the child
            MPI_Send(&msg, 1, MPI_INT, my_rank + step, 0, MPI_COMM_WORLD);
        // Only processes that have to receive the message && checks the processes level
        } else if (my_rank >= step && my_rank < step * 2) {
            // rank - step is the parent
            MPI_Recv(&msg, 1, MPI_INT, my_rank - step, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            printf("Process %d received value %d at step %d\n", my_rank, msg, step);
        }
    }

    MPI_Finalize();
    return 0;
} /* main */
