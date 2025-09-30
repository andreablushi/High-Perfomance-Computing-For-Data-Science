#include <stdio.h>
#include <string.h>   /* For strlen */
#include <stdlib.h>   // For rand(), srand()
#include <mpi.h>      /* For MPI functions */

const int MAX_STRING = 100;

/*
    Task:
    Implement a “reduce” by using send and
    receive + sum over the set of data collected
*/

int main(void) {
    int comm_sz;    /* Number of processes */
    int my_rank;    /* My process rank     */

    MPI_Init(NULL, NULL);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_sz);
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

    // Basic process
    if (my_rank != 0) {
        srand(my_rank);
        int local_value = (rand() % 10) + 1; // Generating a number
        printf("Process %d generated value %d\n", my_rank, local_value);
        MPI_Send(&local_value, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);
    // Master process
    }else{
        int sum = 0;
        int i;
        for (i = 1; i < comm_sz; i++) {
            int recv_val;
            MPI_Recv(&recv_val, 1, MPI_INT, i, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            sum += recv_val;
        }
        printf("Final sum at master process = %d\n", sum);
    }

    MPI_Finalize();
    return 0;
} /* main */
