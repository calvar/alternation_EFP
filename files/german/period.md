## Demonstration: Solving for the Period $T$

To show that $T = N/d$ is the smallest positive integer satisfying the condition, we analyze the properties of modular arithmetic and the greatest common divisor (GCD).

---

### 1. Simplify the Equation
The given condition is:
$$rB \equiv (r + T)B \pmod{N}$$

By distributing $B$ on the right side, we get:
$$rB \equiv rB + TB \pmod{N}$$

Subtracting $rB$ from both sides, the condition simplifies to:
**$$TB \equiv 0 \pmod{N}$$**

### 2. Relate to Divisibility
The statement $TB \equiv 0 \pmod{N}$ implies that $TB$ is a multiple of $N$. We can write this as:
$$TB = kN$$
for some integer $k$.

### 3. Introduce the GCD
We are given that $d = \gcd(N, B)$. We can express $N$ and $B$ in terms of $d$ and two coprime integers:
* $B = d \cdot b'$
* $N = d \cdot n'$
* $\gcd(b', n') = 1$

Substitute these expressions into our divisibility equation:
$$T(d \cdot b') = k(d \cdot n')$$

Divide both sides by $d$:
**$$T \cdot b' = k \cdot n'$$**

### 4. Apply Euclid's Lemma
From the equation $T \cdot b' = k \cdot n'$, we see that $n'$ must divide the product $T \cdot b'$. 

Since we established that $b'$ and $n'$ are **coprime** ($\gcd(b', n') = 1$), **Euclid's Lemma** tells us that $n'$ must divide $T$ ($n' \mid T$).

### 5. Conclusion
The smallest positive integer $T$ that satisfies $n' \mid T$ is $T = n'$. 

Using our substitution $N = d \cdot n'$, we find:
$$T = n' = \frac{N}{d}$$

> **Note:** This confirms that $T = N/d$ is the fundamental period of the sequence under modulo $N$.