#include <stdio.h>
#include <mpi.h>

#define PING_PONG_LIMIT 10

/*
Implement a “ping pong” using send & receive
Two processes one send and one receive each
Run it using: mpirun –n 2
What can we argue about using n>2? There is no need for more process
Would your application be resilient to that? Yes, I check the number of processes
*/

int main(int argc, char** argv) {
    int my_rank, comm_size;
    int ping_pong_count = 0;
    int partner_rank;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_size);

    // Check if there are more than 2 processes
    if(comm_size > 2){
        printf("Too much processes");
        MPI_Finalize();
        return 0;
    }
    
    // Supposing there are only two process, I calculate the other process rank
    partner_rank = (my_rank + 1) % 2;

    // Limiting the number of passes
    while (ping_pong_count < PING_PONG_LIMIT) {
        // First process to start
        if (my_rank == 0) {
            ping_pong_count++;
            MPI_Send(&ping_pong_count, 1, MPI_INT, partner_rank, 0,
                     MPI_COMM_WORLD);
            printf("Process %d sent ping_pong_count %d to process %d\n",
                   my_rank, ping_pong_count, partner_rank);
            MPI_Recv(&ping_pong_count, 1, MPI_INT, partner_rank, 0,
                     MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            printf("Process %d received ping_pong_count %d from process %d\n",
                   my_rank, ping_pong_count, partner_rank);
        // Second process to start
        } else if(my_rank == 1){
            MPI_Recv(&ping_pong_count, 1, MPI_INT, partner_rank, 0,
                     MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            printf("Process %d received ping_pong_count %d from process %d\n",
                   my_rank, ping_pong_count, partner_rank);
            ping_pong_count++;
            MPI_Send(&ping_pong_count, 1, MPI_INT, partner_rank, 0,
                     MPI_COMM_WORLD);
            printf("Process %d sent ping_pong_count %d to process %d\n",
                   my_rank, ping_pong_count, partner_rank);
        }
    }

    MPI_Finalize();
    return 0;
}
