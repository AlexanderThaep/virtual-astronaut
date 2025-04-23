using System.Net;
using System.Net.Sockets;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;

public class UDPVideoReceiver : MonoBehaviour
{
    public int port = 3000; // Match the Python UDP port
    private UdpClient udpClient;
    private IPEndPoint endpoint;
    private Texture2D texture;
    private List<byte> imageBuffer = new List<byte>();
    private byte[] imageData;
    private Thread worker;

    void Start()
    {
        udpClient = new UdpClient(port); // Use IPv4
        endpoint = new IPEndPoint(IPAddress.Any, port);

        texture = Texture2D.blackTexture; // Placeholder size; will update later
        GetComponent<Renderer>().material.mainTexture = texture;

        worker = new Thread(ReceiveVideo);
        worker.Start();
    }

    void Update()
    {
        applyImage();
    }

    void ReceiveVideo()
    {
        while (true)
        {
            byte[] data = udpClient.Receive(ref endpoint);

            if (data.Length == 1) // End-of-frame marker
            {
                // Assemble the full frame
                imageData = imageBuffer.ToArray();
                imageBuffer.Clear();
            }
            else
            {
                // Accumulate chunks into the buffer
                imageBuffer.AddRange(data);
            }
        }
    }

    void applyImage()
    {
        // Decode the image and apply it to the texture
        texture.LoadImage(imageData);
        GetComponent<Renderer>().material.mainTexture = texture;
    }

    void OnDestroy()
    {
        worker.Abort();
        udpClient.Close();
    }
}