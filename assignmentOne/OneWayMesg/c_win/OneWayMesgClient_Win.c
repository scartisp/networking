/*
 * Implementation of one-way message client in C
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

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <server name> <server port>\n", argv[0]);
        return 1;
    }

    char *serverName = argv[1];
    int serverPort = atoi(argv[2]);

    // Initialize Winsock
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        fprintf(stderr, "WSAStartup failed\n");
        return 1;
    }

    // Create a socket
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        fprintf(stderr, "Socket creation failed: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }

    // Resolve server address
    struct sockaddr_in serverAddr;
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(serverPort);

    struct hostent *hostEntry = gethostbyname(serverName);
    if (!hostEntry) {
        fprintf(stderr, "gethostbyname failed\n");
        closesocket(sock);
        WSACleanup();
        return 1;
    }
    memcpy(&serverAddr.sin_addr, hostEntry->h_addr, hostEntry->h_length);

    // Connect to server
    if (connect(sock, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        fprintf(stderr, "Connect failed: %d\n", WSAGetLastError());
        closesocket(sock);
        WSACleanup();
        return 1;
    }
    printf("Connected to server at ('%s', '%d')\n", serverName, serverPort);

    char buffer[MAXMESGLEN];
    while (1) {
        // Read input
        char *line = fgets(buffer, MAXMESGLEN, stdin);
        if (!line) {
            printf("Closing connection\n");
            closesocket(sock);
            break;
        }

        // Send message
        send(sock, buffer, strlen(buffer), 0);
    }

    WSACleanup();
    return 0;
}
