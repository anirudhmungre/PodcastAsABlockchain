import java.util.Date;

public class Block {
    public String hash;
    public String previousHash;
    private String data; // The id of the data item in the DB
    private long timeStamp; // Unix Epoch Time in Milliseconds
    private int nonce;

    //Block Constructor.
    public Block(String data, String previousHash ) {
        this.data = data;
        this.previousHash = previousHash;
        this.timeStamp = new Date().getTime();
        this.hash = calculateHash();
    }

    public String calculateHash() {
        return StringUtil.applySha256(
                previousHash +
                        Long.toString(timeStamp) +
                        Integer.toString(nonce) +
                        data
        );
    }

    public void mineBlock(int difficulty) {
        String target = new String(new char[difficulty]).replace('\0', '0');
        while(!hash.substring(0, difficulty).equals(target)) {
            nonce++;
            hash = calculateHash();
        }
        System.out.println("Block " + hash + " has been mined!");
    }
}
