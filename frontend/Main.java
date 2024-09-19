public class Main{
    public static void main(String[] args) {
        int[] entry ={7,0,5,1,3};
        int[] exit = {1,2,1,3,4};

        int guests=0;
        int max=0;

        for(int i=0;i<entry.length;i++){
            guests += entry[i]-exit[i];
            //System.out.println(guests);
        //    System.out.println(guests);
            max = Math.max(guests,max);
        }
        
        System.out.println(max);
    }
    }
