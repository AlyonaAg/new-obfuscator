function powToMod(base, power, module) {
if (power == 1) return base;
if (power % 2 == 0) return powToMod(base, power / 2, module) ** 2 % module;
return powToMod(base, power - 1, module) * base % module;
}
function TestFerma(n) {
var number = new Array();
var r;
for (i = 0; i <= 7; i++)
number[i] = Math.floor(Math.random() * (n - 4) + 2);
for (i = 0; i <= 7; i++) {
r = powToMod(number[i], n - 1, n);
if (r != 1) {
console.log('Основание ' + number[i]);
console.log('Тест Ферма: число ' + n + ' составное');
return;
}
}
console.log('Тест Ферма: число ' + n + ' вероятно простое');
}
function Euclid(a, b) {
var c, r0, r1, x0, x1, y0, y1, i;
if (b > a)
{
c = b;
b = a;
a = c;
}
a, b = b, a;
r0 = a, r1 = b, x0 = 1, x1 = 0, y0 = 0, y1 = 1, i = 1;
d = 1, x = 0, y = 0;
while (b) {
q = Math.floor(r0 / r1);
r2 = r0 - q * r1;
if (!r2) {
d = r1, x = x1, y = y1;
break;
}
x2 = x0 - q * x1;
y2 = y0 - q * y1;
x0 = x1; x1 = x2;
y0 = y1; y1 = y2;
r0 = r1; r1 = r2;
i++;
}
console.log('НОД: ' + d + '\nКоэффициент при числе ' + a + ': ' + x + '\nКоэффициент при числе ' + b + ': ' + y);
}
choice = prompt('1) Найти НОД двух чисел\n2) Проверить простоту числа\n');
if (choice == 2) {
n = prompt('Введите число');
TestFerma(n);
}
else if (choice == 1) {
var a = prompt('Введите first число');
var b = prompt('Введите второе число');
Euclid(a, b);
}