using UnityEngine;
using Unity.Networking.Transport;
using Unity.Collections;

using System.Collections.Generic;

public class VideoStream2 : MonoBehaviour
{
    public int port = 3000; // Match the Python UDP port
    private NetworkDriver m_Driver;

    private NetworkDriver wsClient;
    private NetworkConnection wsConnect;

    private Texture2D texture;
    private List<byte> imageBuffer = new List<byte>();
    private NativeArray<byte> data;

    //PC: 10.42.0.23
    //RaspberryPi: 10.42.0.23 
    void Start()
    {
        NativeArray<byte> data = new NativeArray<byte>(2048, Allocator.Persistent); 

        NetworkSettings ns = new NetworkSettings();
        ns.WithNetworkConfigParameters(receiveQueueCapacity: 2048);

        m_Driver = NetworkDriver.Create(ns);
        var endpoint = NetworkEndpoint.AnyIpv4;
        endpoint.Port = (ushort) port;
        m_Driver.Bind(endpoint);

        m_Driver.Listen();

        // wsClient = NetworkDriver.Create(new WebSocketNetworkInterface());    
        // wsConnect = default(NetworkConnection);

        // var endpoint = NetworkEndPoint.LoopbackIpv4;
        // endpoint.Port = 8765;
        // m_Connection = m_Driver.Connect(endpoint);

        SendPortInfo(port); 


        texture = new Texture2D(2, 2); // Placeholder size; will update later
    }

    void Update()
    {
        m_Driver.ScheduleUpdate().Complete();

        DataStreamReader stream;

        // Check for incoming data
        while (m_Driver.PopEvent(out var connection, out stream) != NetworkEvent.Type.Empty)
        {
            Debug.Log("Cat");
            if (stream.Length > 0)
            {
                stream.ReadBytes(data);

                if (data.Length == 1) // End-of-frame marker
                {
                    // Assemble the full frame
                    byte[] imageData = imageBuffer.ToArray();
                    imageBuffer.Clear();

                    // Decode the image and apply it to the texture
                    texture.LoadImage(imageData);
                    GetComponent<Renderer>().material.mainTexture = texture;
                }
                else
                {
                    // Accumulate chunks into the buffer
                    imageBuffer.AddRange(data);
                }
            }
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
//       m_Connection.Send(m_Driver, new DataStreamWriter(portBytes.Length, Allocator.Temp) { Write(portBytes) });
//        Debug.Log("Sent port information: " + port);
//    }

//    void OnDestroy()
//    {
//        m_Driver.Dispose(); // Clean up driver when done
//    }
}

