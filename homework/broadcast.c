#include <stdio.h>
#include <string.h>   /* For strlen */
#include <stdlib.h>   // For rand(), srand()
#include <mpi.h>      /* For MPI functions */


/*
    Task:
    Implement a loop-based “broadcast” by using send and
    receive"
*/

int main(void) {
    int comm_sz;    /* Number of processes */
    int my_rank;    /* My process rank     */

    int sum = 9; // Sum variable for the master
    MPI_Init(NULL, NULL);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_sz);
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

    // BROADCAST PART
    if (my_rank == 0){
        int i;
        for (i = 1; i < comm_sz; i++) {
            MPI_Send(&sum, 1, MPI_INT, i, 0, MPI_COMM_WORLD);
        }
        printf("The result has been sent to everyone\n");

    }else{
        // For the other process I receive on the sum variable for convenience
        MPI_Recv(&sum, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("I'm process %d and the result is %d!\n", my_rank, sum);
    }
    // All the prevoius code summarize the AllReduce program

    MPI_Finalize();
    return 0;
} /* main */
