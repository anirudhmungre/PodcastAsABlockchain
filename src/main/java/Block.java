import java.util.Date;

public class Block {
    public String hash;
    public String previousHash;
    private String data; // The id of the data item in the DB
    private long timeStamp; // Unix Epoch Time in Milliseconds

    //Block Constructor.
    public Block(String data,String previousHash ) {
        this.data = data;
        this.previousHash = previousHash;
        this.timeStamp = new Date().getTime();
        this.hash = calculateHash();
    }

    public String calculateHash() {
        return StringUtil.applySha256(
                previousHash +
                        Long.toString(timeStamp) +
                        data
        );
    }
}
