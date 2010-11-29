import java.io.*;
import java.net.Socket;
import java.net.ServerSocket;
import java.util.*;
import java.net.*;
import java.lang.Math;
import java.lang.String;

public class DatGame implements Runnable
{
    Socket socket = null;
    PrintWriter out = null;
    BufferedReader in = null;
    private static ServerSocket sSocket = null;
    private static Vector<Double> person = new Vector<Double>();
    private Vector<Double> randomCandidate = new Vector<Double>();
    private Vector<Double> clientCandidate = new Vector<Double>();
    private int N = 30;
    private boolean ready = false;//server ready to disconnect?
    private static boolean valComplete = false; //person attribute file validation complete?

    private long ctime; //current time
    private long totTime; //total time

    public DatGame(Socket socket, ServerSocket sSocket) 
    {
	this.socket = socket;
	if(this.sSocket == null)
	    this.sSocket = sSocket;

	try 
	    {
		out = new PrintWriter(socket.getOutputStream(), true);
		in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
	    }
	catch (IOException e) 
	    {
		System.err.println("No I/O");
		System.exit(-1);
	    }
    }

    public void run() 
    {
	try 
	    {
		processRequest();
	    }

	catch (Exception e) 
	    {
		System.out.println("Error in run method");
	    }
		
    }

    public void processRequest() 
    {
		
	String inputLine = null;
	try 
	    {
		inputLine = in.readLine();//read client ID 
		
		if(inputLine.equals("Person")) 
		    {
			System.out.println("Interacting with Person");
			out.println("N:" + N);

			totTime = 0;
			ctime = System.currentTimeMillis();
			inputLine = in.readLine();
			totTime += System.currentTimeMillis() - ctime;

			System.out.println("" + inputLine);
			System.out.println("Time taken to generate Person attribute file: " + totTime/1000.0);

			//check for time out
			if(totTime/1000.0 >= 120) //time out
			    {
				out.println("TIME OUT");
				ready = true;
			    }
			else
			    {
				InputStream is = new FileInputStream(inputLine);
				BufferedReader fileinput = new BufferedReader(new InputStreamReader(is));
				
				String fileText;
				int index = 0;
				while (( fileText = fileinput.readLine()) != null) //read contents of Person's file
				    {	
					Double wt = Double.parseDouble(fileText);
					person.add(index,wt);
					index++;
				    }
				//check if file contains N attributes
				System.out.println("N = " + N + "\tindex = " + index);
				if(index != N)
				    {
					out.println("Person file does not contain N attributes");
					out.println("DISCONNECT");
					ready = true;
				    }
				else
				    {
					//verify person's attributes
					double sumPositive = 0;
					double sumNegative = 0;
					for(int i = 0; i < N; i++) 
					    {
						if(person.get(i) < 0) 
						    {
							sumNegative += person.get(i);
						    }
						else
						    sumPositive += person.get(i);
					    }

					if((int)(sumPositive * 100) == 100 && (int)(sumNegative * 100) == -100) 
					    {
						out.println("VALID ATTRIBUTES");
						out.println("DISCONNECT");
						valComplete = true;
					    }
					else 
					    {
						System.out.println("Sum pos " + (int)(sumPositive * 100));
						System.out.println("Sum neg " + (int)(sumNegative * 100));
						out.println("INVALID ATTRIBUTES");
						out.println("DISCONNECT");
					    }
				    }
			    }
		    }

		if(inputLine.equals("Matchmaker")) {
		    if(valComplete) 
			{									
			    System.out.println("Interacting with Matchmaker");
			    out.println("");
			    out.println("N:" + N);
							
			    //generate 20 random candidates
			    Random generator = new Random();
			    double score = 0;
			    int temp;
			    String randCandidate;
							
			    for(int i = 0; i < 20; i++) 
				{
				    for(int k = 0; k < N; k++) 
					{
					    temp = (int)(generator.nextDouble() * 100);//round off to two decimal places
					    randomCandidate.add(k,((double)temp)/100);
									
					}
								
				    randCandidate = Double.toString(randomCandidate.get(0));
				    score = 0;
				    for(int k = 0; k < N; k++) 
					{
					    score = score + (randomCandidate.get(k) * person.get(k));
					    if(k > 0)
						randCandidate = randCandidate.concat(":" + (Double.toString(randomCandidate.get(k))));
									
					}
				    temp = (int) (score * 100);
				    score = ((double)temp)/100;
				    randCandidate = (Double.toString(score)).concat(":" + randCandidate);
				    out.println("" + randCandidate);
				}
						
			    totTime = 0;
			    int cCount = 0;
			    double[] cScore = new double[20];
			    double bestScore = -1;
			    double bestCount = 0;//no. of candidates used to get to the best score
			    String parse[];
							
			    out.println("SCORE:0:0:0");//initial score

			    while (true) //read in candidate vectors until ideal candidate is found or client runs out of candidates
				{
				    ctime = System.currentTimeMillis();
				    inputLine = in.readLine();
				    totTime += System.currentTimeMillis() - ctime;

				    System.out.println("" + inputLine);
								
				    parse = inputLine.split(":");

				    if(parse.length == N) 
					{
					    for(int i = 0; i < N; i++) 
						{
						    clientCandidate.add(i,Double.parseDouble(parse[i]));
						}
								
								
					    cScore[cCount] = 0;
					    for(int i = 0; i < N; i++) //compute score
						{
						    cScore[cCount] += (clientCandidate.get(i) * person.get(i));	
						}
								
					    temp = (int) (cScore[cCount] * 100);
					    cScore[cCount] = ((double)temp)/100;
								
					    if(cScore[cCount] > bestScore) 
						{
						    bestScore = cScore[cCount];
						    bestCount = cCount + 1;
						}
								
					    if((int)(cScore[cCount] * 100) == 100) //ideal candidate found
						{
						    out.println("IDEAL CANDIDATE FOUND");
						    out.println("FINAL SCORE:" + cScore[cCount] + ":"+ bestScore + ":" + bestCount); 
						    out.println("DISCONNECT");
						    ready = true;
						    break;
						}
								
					    if(cCount == 19) //20 candidates generated
						{
						    out.println("NO MORE CANDIDATES");
						    out.println("FINAL SCORE:" + cScore[cCount] + ":" + bestScore + ":" + bestCount); 
						    out.println("DISCONNECT");
						    ready = true;
						    break;
						}

					    if(totTime/1000.0 >= 120) //time out
						{
						    out.println("TIME OUT");
						    ready = true;
						    break;
						}
					    else
						System.out.println("Time elapsed: " + totTime/1000.0);
								
					    out.println("SCORE:" + cScore[cCount] + ":" + bestScore + ":" + (cCount + 1));//send updated score vector
					    cCount++;
					}
				    else 
					{
					    out.println("Candidate vector does not contain N attributes");
					    out.println("DISCONNECT");
					    ready = true;
					    break;
					}
								
				}
			}
		    else
			{
			    out.println("");
			    out.println("Matchmaker logged in early");
			    out.println("DISCONNECT");
			    ready = true;
			}
		}
	    }
	catch (IOException e) {
	    System.out.println("IO Exception: " + e);
	    System.exit(-1);
	}
	finally {
	    try	{
		out.close();
		in.close();
		socket.close();

		if(ready == true)
		    {
			System.out.println("Server disconnecting ... ");
			sSocket.close();
		    }

	    }
	    catch(IOException e) {
		System.out.println("IO Exception: " + e);
		System.exit(-1);
	    }
	}
    }
}


