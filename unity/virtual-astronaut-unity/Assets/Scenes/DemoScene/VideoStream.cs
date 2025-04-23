using System.Collections.Generic;
using System.Threading;
using System.Net;
using System.Net.Sockets;

using UnityEngine;
using Unity.Collections;

// https://docs.unity3d.com/Packages/com.unity.transport@2.5/api/Unity.Networking.Transport.NetworkDriver.html
// https://discussions.unity.com/t/can-transport-be-used-on-the-client-to-connect-with-a-generic-tcp-socket-server/867873
// Transports library does not support raw UDP

public class VideoStream2 : MonoBehaviour
{
    private Texture2D texture;
    private byte[] imageData;
    private List<byte> imageBuffer = new List<byte>();
    private bool imageReady = false;

    private UdpClient client;
    private Thread receiveThread;
    private bool isRunning = false;
    private bool isConnected = false;

    private string serverIP = "10.42.0.1";  // The IP address of the server
    private ushort serverPort = 8765;        // The port number for the connection

    public string clientAddr = "10.42.0.23";  // The IP address of the client
    public ushort clientPort = 3000;         // The client port number for the connection

    void ReceiveData()
    {
        IPEndPoint remoteEndPoint = new IPEndPoint(IPAddress.Any, 0);

        while (isRunning)
        {
            try
            {
                byte[] data = client.Receive(ref remoteEndPoint);
                if (data.Length == 1) // End-of-frame marker
                {
                    // Assemble the full frame
                    imageData = imageBuffer.ToArray();
                    imageBuffer.Clear();
                    imageReady = true;
                }
                else
                {
                    // Accumulate chunks into the buffer
                    imageBuffer.AddRange(data);
                }
            }
            catch (SocketException ex)
            {
                Debug.LogError("Socket exception: " + ex.Message);
            }
        }
    }

    void Start()
    {
        NativeArray<byte> data = new NativeArray<byte>(2048, Allocator.Persistent); 

        client = new UdpClient(clientPort);
        isRunning = true;

        receiveThread = new Thread(ReceiveData);
        receiveThread.IsBackground = true;
        receiveThread.Start();

        texture = new Texture2D(2, 2); // Placeholder size; will update later
    }

    void Update()
    {
        if (imageReady) {
            // Decode the image and apply it to the texture
            texture.LoadImage(imageData);
            GetComponent<Renderer>().material.mainTexture = texture;
            imageReady = false;
        }
    }

    void OnApplicationQuit()
    {
        isRunning = false;
        if (receiveThread != null && receiveThread.IsAlive)
            receiveThread.Abort();

        if (client != null)
            client.Close();
    }
}

// async void ReceiveVideo()
// {
//     while (true)
//     {
//         var result = await udpClient.ReceiveAsync();
//         byte[] data = result.Buffer;

//         if (data.Length == 1) // End-of-frame marker
//         {
//             // Assemble the full frame
//             byte[] imageData = imageBuffer.ToArray();
//             imageBuffer.Clear();

//             // Decode the image and apply it to the texture
//             texture.LoadImage(imageData);
//             GetComponent<Renderer>().material.mainTexture = texture;
//         }
//         else
//         {
//             // Accumulate chunks into the buffer
//             imageBuffer.AddRange(data);
//         }
//     }
// }

//    void SendPortInfo(int port)
//    {
//        byte[] portBytes = System.BitConverter.GetBytes(port); // Convert port to byte array
//        m_Connection.Send(m_Driver, new DataStreamWriter(portBytes.Length, Allocator.Temp) { Write(portBytes) });
//        Debug.Log("Sent port information: " + port);
//    }