@a = global i32 10;
define i32 @f(i32 %x) {
%1 = mul i32 10, 2
%2 = load i32, i32* @a
%3 = add i32 %2, %1
ret i32 %3
}
define i32 @f2(i32 %x) {
%1 = call i32 @f(i32 %x)
%2 = sub i32 %1, 5
ret i32 %2
}
