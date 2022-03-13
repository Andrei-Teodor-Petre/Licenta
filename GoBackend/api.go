package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

type packet struct {
	//this should have some data
	//some id number
	//some order number
	//some
}

// getAlbums responds with the list of all albums as JSON.
func getAlbums(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, "hello world!")
}

func main() {
	router := gin.Default()
	//define all the routes here
	router.GET("/hello", getAlbums)


	//run after all the routes are defined
	router.Run("localhost:8080")
}
