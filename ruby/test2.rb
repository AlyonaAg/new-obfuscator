class NumberTheory
  def pow_to_mod(base, power, mod)
    return base if power == 1

    if power % 2 == 0
      return pow_to_mod(base, power / 2, mod) ** 2 % mod
    else
      return pow_to_mod(base, power - 1, mod) * base % mod
    end
  end

  def test_ferma(n)
    numbers = Array.new(8) { rand(2...(n - 4)) + 2 }

    numbers.each do |number|
      r = pow_to_mod(number, n - 1, n)
      if r != 1
        puts "Base #{number}"
        puts "Ferma: number #{n} not simple"
        return
      end
    end

    puts "Ferma: number #{n} simple"
  end

  def euclid(a, b)
    puts "#{a} #{b}"
    if b > a
      a, b = b, a
    end

    r0, r1, x0, x1, y0, y1 = a, b, 1, 0, 0, 1

    while b != 0
      q = r0 / r1
      r2 = r0 - q * r1

      if r2.zero?
        d = r1
        x = x1
        y = y1
        break
      end

      x2 = x0 - q * x1
      y2 = y0 - q * y1

      x0, x1 = x1, x2
      y0, y1 = y1, y2
      r0, r1 = r1, r2
    end

    puts "NOD: #{d}\nKoeff #{a}: #{x}\nKoeff #{b}: #{y}"
  end
end

number_theory = NumberTheory.new

choice = gets.chomp.to_i

if choice == 2
  n = gets.chomp.to_i
  number_theory.test_ferma(n)
elsif choice == 1
  a = gets.chomp.to_i
  b = gets.chomp.to_i
  number_theory.euclid(a, b)
end
