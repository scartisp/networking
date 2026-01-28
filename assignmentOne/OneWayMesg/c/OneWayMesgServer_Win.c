/*
 * Implementation of one-way message server in C
 * Modificationns added for Windows 11 compilation with VS 2022
 */

#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib") // Link with Ws2_32.lib

#define MAXMESGLEN  1024

// Function to receive a message from the client
char *recvMesg(SOCKET sd, char *mesg) {
    char *ptr = mesg;
    while (1) {
        int nread = recv(sd, ptr, 1, 0);
        if (nread == SOCKET_ERROR) {
            fprintf(stderr, "Recv failed: %d\n", WSAGetLastError());
            exit(1);
        }
        if (nread == 0)
            return NULL; // Client closed connection
        if (*ptr == '\n') {
            *(ptr + 1) = 0; // Null-terminate the string
            break;
        }
        ptr++;
    }
    return mesg;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <port>\n", argv[0]);
        return 1;
    }

    int serverPort = atoi(argv[1]);

    // Initialize Winsock
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        fprintf(stderr, "WSAStartup failed\n");
        return 1;
    }

    // Create the server socket
    SOCKET serverSock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (serverSock == INVALID_SOCKET) {
        fprintf(stderr, "Socket creation failed: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }

    // Allow reuse of the port
    int opt = 1;
    if (setsockopt(serverSock, SOL_SOCKET, SO_REUSEADDR, (const char*)&opt, sizeof(opt)) == -1) {
        fprintf(stderr, "setsockopt failed: %d\n", WSAGetLastError());
        closesocket(serverSock);
        WSACleanup();
        return 1;
    }

    // Bind the socket to the given port
    struct sockaddr_in serverAddr;
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(serverPort);

    if (bind(serverSock, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) == -1) {
        fprintf(stderr, "Bind failed: %d\n", WSAGetLastError());
        closesocket(serverSock);
        WSACleanup();
        return 1;
    }

    // Start listening for incoming connections
    if (listen(serverSock, 5) == SOCKET_ERROR) {
        fprintf(stderr, "Listen failed: %d\n", WSAGetLastError());
        closesocket(serverSock);
        WSACleanup();
        return 1;
    }
    printf("Waiting for a client...\n");

    // Accept a client connection
    struct sockaddr_in clientAddr;
    int clientAddrLen = sizeof(clientAddr);
    SOCKET clientSock = accept(serverSock, (struct sockaddr*)&clientAddr, &clientAddrLen);
    if (clientSock == INVALID_SOCKET) {
        fprintf(stderr, "Accept failed: %d\n", WSAGetLastError());
        closesocket(serverSock);
        WSACleanup();
        return 1;
    }

    char clientIP[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &clientAddr.sin_addr, clientIP, sizeof(clientIP));
    printf("Connected to client at ('%s', '%d')\n", clientIP, ntohs(clientAddr.sin_port));

    // Close the server socket since no other clients are being handled
    closesocket(serverSock);

    // Communicate with the client
    char buffer[MAXMESGLEN];
    while (1) {
        char *message = recvMesg(clientSock, buffer);
        if (!message) {
            printf("Client closed connection\n");
            closesocket(clientSock);
            break;
        }
        printf("Client: %s", message);
    }

    // Clean up Winsock
    WSACleanup();
    return 0;
}

