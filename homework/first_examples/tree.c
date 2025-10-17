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

    // If not the root, I receive from the parent
    if (my_rank != 0) {
        int parent = (my_rank - 1) / 2;   // rule: parent(i) = (i-1)/2
        MPI_Recv(&msg, 1, MPI_INT, parent, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("Process %d received value %d from parent %d\n", my_rank, msg, parent);
    // If root, I print the starting message
    } else {
        printf("Process %d starts with value %d\n", my_rank, msg);
    }

    // Calculate children ranks
    int left_child  = 2 * my_rank + 1;
    int right_child = 2 * my_rank + 2;

    // If children exist, send them the message
    if (left_child < comm_sz) {
        MPI_Send(&msg, 1, MPI_INT, left_child, 0, MPI_COMM_WORLD);
    }
    if (right_child < comm_sz) {
        MPI_Send(&msg, 1, MPI_INT, right_child, 0, MPI_COMM_WORLD);
    }

    MPI_Finalize();
    return 0;
} /* main */
