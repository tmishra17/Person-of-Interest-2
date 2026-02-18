import 'dart:convert';
import 'dart:developer';
import 'package:flutter/material.dart';
import 'dart:io';
import "package:http/http.dart" as http;

void main() {
  runApp(POIMobileApp());
}
class POIMobileApp extends StatefulWidget {
  const POIMobileApp({super.key});

  @override
  State<POIMobileApp> createState() => _POIMobileAppState();
}
String getBaseUrl() {
  if (Platform.isAndroid) {
    return 'http://10.0.2.2:8000';
  }
  else {
    return 'http://localhost:8000';
  }
}
class _POIMobileAppState extends State<POIMobileApp> {
  @override
  double numResults = 10; // default value
  double simScore = 0.2;
  String baseUrl = getBaseUrl();
  List<Map<String, dynamic>> searchResults = [];
  Future<void> getSearchResults(String query) async {
    log("Called this function and it worked successfully");
    try {
      final res = await http.get(Uri.parse('$baseUrl/search').replace(queryParameters: {
        "query": query,
        "sim_score": simScore.toString(),
        "results": numResults.toInt().toString()
      }));
      if (res.statusCode == 200) {
        // get json strings from the list of searchResults
        setState(() {
          searchResults = List<Map<String, dynamic>>.from(
            jsonDecode(res.body)
          );
        });
      }
      else {
        throw Exception('Failed to load data. Status code: ${res.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to connect to the server: $e');
    }

  }
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        backgroundColor: const Color.fromARGB(255, 50, 50, 50),
        appBar: AppBar(
            backgroundColor: const Color.fromARGB(255, 93, 93, 93),
            title: const Text("Person Of Interest"),
            titleTextStyle: TextStyle(
              color: const Color.fromRGBO(255, 255, 255, 1.0),
              fontSize: 24
            ),
          ),
          body: Column(
            children: [
              // Then in your Column, add:
              Container(
                
                // color: const Color.fromARGB(31, 0, 0, 0),
                // title:  const Text("Person Of Interest")
                margin: EdgeInsets.symmetric(horizontal: 10, vertical: 50),
                child: TextField(
                  textInputAction: TextInputAction.search,
                  decoration: InputDecoration(
                    hintText: "Enter a description",
                    hintStyle: TextStyle(color: Colors.grey),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(30.0)
                    ),
                    filled: true,
                    fillColor: Colors.white,
                    
                  ),
                  onSubmitted: (query) => {
                    getSearchResults(query)
                  },
                ),
                ),
            // Slider for selecting number of results
            StatefulBuilder(
              builder: (BuildContext context, StateSetter setState) {
                
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    Text(
                      'Number of results: ${numResults.toInt()}',
                      style: TextStyle(color: Colors.white),
                      // margin: EdgeInsets.symmetric(horizontal: 10)
                    ),
                    Slider(
                      min: 1,
                      max: 50,
                      divisions: 49,
                      value: numResults,
                      label: numResults.round().toString(),
                      activeColor: Colors.blueAccent,
                      onChanged: (double value) {
                        setState(() => numResults = value);
                      },
                    ),
                    Text(
                      'Similarity Threshold: $simScore',
                      style: TextStyle(color: Colors.white),
                      // margin: EdgeInsets.symmetric(horizontal: 10)
                    ),
                    Slider(
                      min: 0.0,
                      max: 0.5,
                      value: simScore,
                      divisions: 10,
                      label: simScore.toDouble().toString(),
                      activeColor: Colors.blueAccent,
                      onChanged: (double value) {
                        setState(() => simScore = value);
                      },
                    ),
                  ],
                );
              }
            ),
            
              // take up all of the space of the column
              Expanded( 
                child: GridView.builder(
                  physics: const BouncingScrollPhysics(),
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 3,
                    childAspectRatio: 0.75,  // width/height of each cell (e.g. 0.75 = slightly taller)
                    mainAxisSpacing: 8,
                    crossAxisSpacing: 9,
                  ),
                  itemCount: searchResults.length,
                  itemBuilder: (context, index) {
                    final data = searchResults[index];
                    final imageUrl = baseUrl + data['image_url'];
                    return Column(
                      children: [
                        Expanded(
                          child: Container(
                            width: double.infinity,
                            padding: EdgeInsets.all(10),
                            // margin: EdgeInsets.symmetric(vertical: 100),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(15.0),
                              child: Image.network(imageUrl,
                                fit: BoxFit.cover,
                                width: double.infinity,
                                height: double.infinity,
                                
                              ),
                            ),
                          ),
                        ),
                        Text(
                          "Similarity Score: $simScore",
                          style: TextStyle(color: Colors.white),
                        )
                      ],
                    );
                  },
                ),
              ),
            ],
          ),
      ),
    );
  }
}