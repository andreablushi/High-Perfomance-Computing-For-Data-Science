#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpi.h>

#define MAX_SIZE (1 << 20) // 1 MiB

/*
Implement a simple send-receive benchmark to measure time and bandwidth for message sizes 1,2,3,4.... up to max-size 1MB.
This simple exercise
*/
int main(int argc, char** argv) {
    int my_rank, comm_size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_size);

    // Check if there are more than 2 processes
    // Recycled from pingpong
    if(comm_size > 2){
        printf("Too much processes");
        MPI_Finalize();
        return 0;
    }

    // Setting the CSV
    /* Header for output (CSV) */
    if (my_rank == 0) {
        printf("# n, time(sec), RATE(MB/SEC)\n");
        fflush(stdout);
    }

    size_t size;
    /* Loop over message sizes doubling each time: 1,2,4,... up to max_size */
    for (size = 1; size <= MAX_SIZE; size <<= 1) {
        char *buf = (char*) malloc(size);
        if (!buf) {
            fprintf(stderr, "Rank %d: malloc failed for size %zu\n", my_rank, size);
            MPI_Abort(MPI_COMM_WORLD, 1);
        }
        /* Starting the timer*/
        double t_start = MPI_Wtime();
        // Communication
        if (my_rank == 0) {
            MPI_Send(buf, (int)size, MPI_BYTE, 1, 200, MPI_COMM_WORLD);
            MPI_Recv(buf, (int)size, MPI_BYTE, 1, 200, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        } else {
            MPI_Recv(buf, (int)size, MPI_BYTE, 0, 200, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            MPI_Send(buf, (int)size, MPI_BYTE, 0, 200, MPI_COMM_WORLD);
        }
        /* Stopping timer*/
        double t_end = MPI_Wtime();

        // Calculation
        double time = t_end - t_start; // Total time used
        double one_way = time / 2.0;    // Cost of a single send-rcv pair
        double size_MB = ((double)size) / (1024.0 * 1024.0);   // Current size considered
        double rate = (one_way > 0.0) ? (size_MB / one_way) : 0.0;  // Calculating the bandwidth

        /* Print results on the casv from rank 0 (single consolidated output) */
        if (my_rank == 0) {
            printf("%zu, %.9f, %.6f\n", size, time, rate);
            fflush(stdout);
        }

        free(buf);
    }

    MPI_Finalize();
    return 0;
}
