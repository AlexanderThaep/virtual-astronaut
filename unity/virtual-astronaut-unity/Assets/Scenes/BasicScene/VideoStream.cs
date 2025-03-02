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

    void Start()
    {
        NativeArray<byte> data = new NativeArray<byte>(2048, Allocator.Persistent); 

        NetworkSettings ns = new NetworkSettings();
        ns.WithNetworkConfigParameters(receiveQueueCapacity: 2048);

        m_Driver = NetworkDriver.Create(ns);
        var endpoint = NetworkEndpoint.LoopbackIpv4;
        endpoint.Port = (ushort) port;
        m_Driver.Bind(endpoint);

        m_Driver.Listen();

        // wsClient = NetworkDriver.Create(new WebSocketNetworkInterface());    
        // wsConnect = default(NetworkConnection);

        // var endpoint = NetworkEndPoint.LoopbackIpv4;
        // endpoint.Port = 8765;
        // m_Connection = m_Driver.Connect(endpoint);

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
}