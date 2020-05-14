int c[3] = {1,2,3};

int sum(int a, int b);

int main(){
    print(c);
    print("Hello");
    c = sum(c[0], c[1]);
    float aee = (float) c;
    print(aee);
}

int sum(int a, int b){
    int d = a + b;
    return d;
}