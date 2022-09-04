pragma solidity >=0.4.0 <0.7.0;

contract Server{
	uint public vidCount = 0;

	struct Video{
		uint id;
		string content;
		bool minted;
	}

	mapping(uint => Video) public videos; //this gets a free read function

	function addVideo(string memory _content) public{
		vidCount ++;
		videos[vidCount] = Video(vidCount, _content, false);
	}

	

}