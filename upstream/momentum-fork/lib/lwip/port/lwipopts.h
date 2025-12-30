#ifndef __LWIPOPTS_H__
#define __LWIPOPTS_H__

// Operating System mode
#define NO_SYS               0
#define SYS_LIGHTWEIGHT_PROT 1

// Memory configuration
#define MEM_ALIGNMENT            4
#define MEM_SIZE                 (16 * 1024)
#define MEMP_NUM_PBUF            16
#define MEMP_NUM_UDP_PCB         6
#define MEMP_NUM_TCP_PCB         10
#define MEMP_NUM_TCP_PCB_LISTEN  5
#define MEMP_NUM_TCP_SEG         24
#define MEMP_NUM_SYS_TIMEOUT     10
#define MEMP_NUM_NETBUF          8
#define MEMP_NUM_NETCONN         10
#define MEMP_NUM_TCPIP_MSG_API   8
#define MEMP_NUM_TCPIP_MSG_INPKT 8

// Pbuf configuration
#define PBUF_POOL_SIZE    16
#define PBUF_POOL_BUFSIZE 512

// Network Interfaces
#define LWIP_NETIF_HOSTNAME        1
#define LWIP_NETIF_STATUS_CALLBACK 1
#define LWIP_NETIF_LINK_CALLBACK   1

// Protocols
#define LWIP_TCP      1
#define TCP_TTL       255
#define LWIP_ARP      1
#define LWIP_ETHERNET 1
#define LWIP_ICMP     1
#define LWIP_DHCP     1
#define LWIP_UDP      1
#define LWIP_DNS      1

// Threading options
#define TCPIP_THREAD_NAME         "TcpIp"
#define TCPIP_THREAD_STACKSIZE    2048
#define TCPIP_THREAD_PRIO         2 // Low priority? Or higher?
#define TCPIP_MBOX_SIZE           8
#define DEFAULT_TCP_RECVMBOX_SIZE 8
#define DEFAULT_UDP_RECVMBOX_SIZE 8
#define DEFAULT_ACCEPTMBOX_SIZE   8

// Checksums - handled by software for now unless hardware support added
#define CHECKSUM_GEN_IP     1
#define CHECKSUM_GEN_UDP    1
#define CHECKSUM_GEN_TCP    1
#define CHECKSUM_GEN_ICMP   1
#define CHECKSUM_CHECK_IP   1
#define CHECKSUM_CHECK_UDP  1
#define CHECKSUM_CHECK_TCP  1
#define CHECKSUM_CHECK_ICMP 1

#define LWIP_TIMEVAL_PRIVATE   0
#define LWIP_ERRNO_STDINCLUDE  1
#define LWIP_SOCKET_STDINCLUDE 1

#endif /* __LWIPOPTS_H__ */
