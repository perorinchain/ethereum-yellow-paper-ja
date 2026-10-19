[分割版目次](../README.md) | [前へ](appendix-g-fee-schedule.md) | [次へ](appendix-i-genesis-block.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="app:vm"></span>

# 付録H. 仮想マシン仕様

256ビットのバイナリ値を整数として解釈する場合、その表現はビッグエンディアンである。

256ビットのマシン・データを160ビットのアドレスまたはハッシュとの間で変換する場合、右側（ビッグエンディアンでは下位）の20バイトを使用し、左端の12バイトを破棄またはゼロで埋める。したがって、バイトをビッグエンディアンとして解釈した整数値は等価である。

## H.1. Gas コスト

一般gasコスト関数 $`C`$ を次のように定義する。

<span id="eq-326"></span>

```math
C(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \equiv C_{\mathrm{mem}}(\boldsymbol{\mu}'_{\mathrm{i}})-C_{\mathrm{mem}}(\boldsymbol{\mu}_{\mathrm{i}}) + \begin{cases}
C_\text{SSTORE}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) & \text{if} \quad w = \text{SSTORE} \\
G_{\mathrm{exp}} & \text{if} \quad w = \text{EXP} \wedge \boldsymbol{\mu}_{\mathbf{s}}[1] = 0 \\
G_{\mathrm{exp}} + G_{\mathrm{expbyte}}\times(1+\lfloor\log_{256}(\boldsymbol{\mu}_{\mathbf{s}}[1])\rfloor) & \text{if} \quad w = \text{EXP} \wedge \boldsymbol{\mu}_{\mathbf{s}}[1] > 0 \\
G_{\mathrm{verylow}} + G_{\mathrm{copy}}\times\lceil\boldsymbol{\mu}_{\mathbf{s}}[2] \div 32\rceil & \text{if} \quad w \in W_{\mathrm{copy}} \\
C_{\mathrm{aaccess}}(\boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}, A) + G_{\mathrm{copy}}\times\lceil\boldsymbol{\mu}_{\mathbf{s}}[3] \div 32\rceil & \text{if} \quad w = \text{EXTCODECOPY} \\
C_{\mathrm{aaccess}}(\boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}, A) & \text{if} \quad w \in W_{\mathrm{extaccount}}\\
G_{\mathrm{log}}+G_{\mathrm{logdata}}\times\boldsymbol{\mu}_{\mathbf{s}}[1] & \text{if} \quad w = \text{LOG0} \\
G_{\mathrm{log}}+G_{\mathrm{logdata}}\times\boldsymbol{\mu}_{\mathbf{s}}[1]+G_{\mathrm{logtopic}} & \text{if} \quad w = \text{LOG1} \\
G_{\mathrm{log}}+G_{\mathrm{logdata}}\times\boldsymbol{\mu}_{\mathbf{s}}[1]+2G_{\mathrm{logtopic}} & \text{if} \quad w = \text{LOG2} \\
G_{\mathrm{log}}+G_{\mathrm{logdata}}\times\boldsymbol{\mu}_{\mathbf{s}}[1]+3G_{\mathrm{logtopic}} & \text{if} \quad w = \text{LOG3} \\
G_{\mathrm{log}}+G_{\mathrm{logdata}}\times\boldsymbol{\mu}_{\mathbf{s}}[1]+4G_{\mathrm{logtopic}} & \text{if} \quad w = \text{LOG4} \\
C_\text{CALL}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) & \text{if} \quad w \in W_{\mathrm{call}} \\
C_\text{SELFDESTRUCT}(\boldsymbol{\sigma}, \boldsymbol{\mu}) & \text{if} \quad w = \text{SELFDESTRUCT} \\
G_{\mathrm{create}} + R(\boldsymbol{\mu}_{\mathbf{s}}[2]) & \text{if} \quad w = \text{CREATE}\\
G_{\mathrm{create}}+G_{\mathrm{keccak256word}} \times \lceil \boldsymbol{\mu}_{\mathbf{s}}[2] \div 32 \rceil + R(\boldsymbol{\mu}_{\mathbf{s}}[2]) & \text{if} \quad w = \text{CREATE2}\\
G_{\mathrm{keccak256}}+G_{\mathrm{keccak256word}} \times \lceil \boldsymbol{\mu}_{\mathbf{s}}[1] \div 32 \rceil & \text{if} \quad w = \text{KECCAK256}\\
G_{\mathrm{jumpdest}} & \text{if} \quad w = \text{JUMPDEST}\\
C_\text{SLOAD}(\boldsymbol{\mu}, A, I) & \text{if} \quad w = \text{SLOAD}\\
G_{\mathrm{zero}} & \text{if} \quad w \in W_{\mathrm{zero}}\\
G_{\mathrm{base}} & \text{if} \quad w \in W_{\mathrm{base}}\\
G_{\mathrm{verylow}} & \text{if} \quad w \in W_{\mathrm{verylow}}\\
G_{\mathrm{low}} & \text{if} \quad w \in W_{\mathrm{low}}\\
G_{\mathrm{mid}} & \text{if} \quad w \in W_{\mathrm{mid}}\\
G_{\mathrm{high}} & \text{if} \quad w \in W_{\mathrm{high}}\\
G_{\mathrm{blockhash}} & \text{if} \quad w = \text{BLOCKHASH}\\
\end{cases} \qquad \text{(326)}
```

<span id="eq-327"></span>

```math
w \equiv \begin{cases} I_{\mathbf{b}}[\boldsymbol{\mu}_{\mathrm{pc}}] & \text{if} \quad \boldsymbol{\mu}_{\mathrm{pc}} < \lVert I_{\mathbf{b}} \rVert\\
\text{STOP} & \text{otherwise}
\end{cases} \qquad \text{(327)}
```

ここで、

<span id="eq-328"></span>

```math
C_{\mathrm{mem}}(a) \equiv G_{\mathrm{memory}} \cdot a + \left\lfloor \dfrac{a^2}{512} \right\rfloor \qquad \text{(328)}
```

<span id="eq-329"></span>

```math
C_{\mathrm{aaccess}}(x, A) \equiv
\begin{cases}
G_{\mathrm{warmaccess}}        & \text{if} \quad x \in A_{\mathbf{a}}\\
G_{\mathrm{coldaccountaccess}} & \text{otherwise}
\end{cases} \qquad \text{(329)}
```

なお、 $`C_\text{CALL}`$ 、 $`C_\text{SELFDESTRUCT}`$ 、 $`C_\text{SLOAD}`$ 、 $`C_\text{SSTORE}`$ は、後続の該当箇所で規定するとおりである。命令の部分集合を次のように定義する。

$`W_{\mathrm{zero}}`$ = {STOP, RETURN, REVERT}

$`W_{\mathrm{base}}`$ = {ADDRESS, ORIGIN, CALLER, CALLVALUE, CALLDATASIZE, CODESIZE, GASPRICE, COINBASE, TIMESTAMP, NUMBER, PREVRANDAO, GASLIMIT, CHAINID, RETURNDATASIZE, POP, PC, MSIZE, GAS, BASEFEE, PUSH0}

$`W_{\mathrm{verylow}}`$ = {ADD, SUB, NOT, LT, GT, SLT, SGT, EQ, ISZERO, AND, OR, XOR, BYTE, SHL, SHR, SAR, CALLDATALOAD, MLOAD, MSTORE, MSTORE8, PUSH1, ..., PUSH32, DUP\*, SWAP\*}

$`W_{\mathrm{low}}`$ = {MUL, DIV, SDIV, MOD, SMOD, SIGNEXTEND, SELFBALANCE}

$`W_{\mathrm{mid}}`$ = {ADDMOD, MULMOD, JUMP}

$`W_{\mathrm{high}}`$ = {JUMPI}

$`W_{\mathrm{copy}}`$ = {CALLDATACOPY, CODECOPY, RETURNDATACOPY}

$`W_{\mathrm{call}}`$ = {CALL, CALLCODE, DELEGATECALL, STATICCALL}

$`W_{\mathrm{extaccount}}`$ = {BALANCE, EXTCODESIZE, EXTCODEHASH}

メモリ・コスト成分に注意されたい。これは $`G_{\mathrm{memory}}`$ と、0および、読み書きを問わずすべてのアクセスが妥当なメモリを参照するために、現在のワード数 $`\boldsymbol{\mu}_{\mathrm{i}}`$ を超えてメモリに必要となるサイズのワード数を切り上げた値との最大値の積として与えられる。このようなアクセスのバイト数はゼロであってはならない。

長さゼロの範囲を参照しても（たとえばCALLへの入力範囲として渡そうとしても）、その範囲の先頭までメモリを拡張する必要はない。 $`\boldsymbol{\mu}'_{\mathrm{i}}`$ は、アクティブ・メモリの新たな最大ワード数として定義される。両者が等しくならない場合は、特例を示す。

$`C_{\mathrm{mem}}`$ がメモリ・コスト関数であることにも注意されたい（拡張関数は拡張前後のコスト差である）。これは高次の項を除算して切り捨てる多項式であるため、使用メモリ704Bまでは線形であり、それを超えるとコストが大幅に増加する。

命令セットの定義にあたり、範囲に対するメモリ拡張関数 $`M`$ を次のように定義する。

<span id="eq-330"></span>

```math
M(s, f, l) \equiv \begin{cases}
s & \text{if} \quad l = 0 \\
\max(s, \left\lceil  (f + l) \div 32  \right\rceil) & \text{otherwise}
\end{cases} \qquad \text{(330)}
```

もう一つ有用な関数として、「64分の1を除く」関数 $`L`$ を次のように定義する。

<span id="eq-331"></span>

```math
L(n) \equiv n - \lfloor n / 64 \rfloor \qquad \text{(331)}
```

<span id="subsec:instruction-set"></span>

## H.2. 命令セット

[第9節](../chapters/09-execution-model.md#ch:model)で先に規定したとおり、これらの定義は同節の最終的な文脈で行われる。特に、 $`O`$ をEVM状態進行関数と仮定し、次サイクルの状態 $`(\boldsymbol{\sigma}', \boldsymbol{\mu}')`$ に関する項を次のように定義する。

<span id="eq-332"></span>

```math
O(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \equiv (\boldsymbol{\sigma}', \boldsymbol{\mu}', A', I) \quad \text{ただし、後述の例外を除く} \qquad \text{(332)}
```

ここでは、[第9節](../chapters/09-execution-model.md#ch:model)の状態遷移規則に対する命令ごとの各種例外と、命令固有の $`J`$ および $`C`$ の追加定義を示す。また各命令について、同節で定義した、スタックへ追加する項目数 $`\alpha`$ とスタックから取り除く項目数 $`\delta`$ も示す。

**0x00番台：停止と算術演算**

特に断りのない限り、すべての算術演算は $`2^{256}`$ を法として行う。ゼロのゼロ乗 $`0^0`$ は1と定義する。

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0x00 | <span id="stop"></span>STOP | 0 | 0 | 実行を停止する。 |
| 0x01 | ADD | 2 | 1 | 加算演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathbf{s}}[0] + \boldsymbol{\mu}_{\mathbf{s}}[1]`$ |
| 0x02 | MUL | 2 | 1 | 乗算演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathbf{s}}[0] \times \boldsymbol{\mu}_{\mathbf{s}}[1]`$ |
| 0x03 | SUB | 2 | 1 | 減算演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathbf{s}}[0] - \boldsymbol{\mu}_{\mathbf{s}}[1]`$ |
| 0x04 | DIV | 2 | 1 | 整数除算演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases}0 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[1] = 0\\ \lfloor\boldsymbol{\mu}_{\mathbf{s}}[0] \div \boldsymbol{\mu}_{\mathbf{s}}[1]\rfloor & \text{otherwise}\end{cases}`$ |
| 0x05 | SDIV | 2 | 1 | 符号付き整数除算演算（ゼロ方向への丸め）。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases}0 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[1] = 0\\ -2^{255} & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[0] = -2^{255} \wedge \, \boldsymbol{\mu}_{\mathbf{s}}[1] = -1\\ \mathbf{sgn} (\boldsymbol{\mu}_{\mathbf{s}}[0] \div \boldsymbol{\mu}_{\mathbf{s}}[1]) \lfloor \vert \boldsymbol{\mu}_{\mathbf{s}}[0] \div \boldsymbol{\mu}_{\mathbf{s}}[1]\vert  \rfloor & \text{otherwise}\end{cases}`$ ここでは、すべての値を2の補数表現の符号付き256ビット整数として扱う。 $`-2^{255}`$ を符号反転するときのオーバーフローの意味論に注意されたい。 |
| 0x06 | MOD | 2 | 1 | 剰余演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases}0 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[1] = 0\\ \boldsymbol{\mu}_{\mathbf{s}}[0] \bmod \boldsymbol{\mu}_{\mathbf{s}}[1] & \text{otherwise}\end{cases}`$ |
| 0x07 | SMOD | 2 | 1 | 符号付き剰余演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases}0 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[1] = 0\\ \mathbf{sgn} (\boldsymbol{\mu}_{\mathbf{s}}[0]) (\vert \boldsymbol{\mu}_{\mathbf{s}}[0]\vert  \bmod \vert \boldsymbol{\mu}_{\mathbf{s}}[1]\vert ) & \text{otherwise}\end{cases}`$ ここでは、すべての値を2の補数表現の符号付き256ビット整数として扱う。 |
| 0x08 | ADDMOD | 3 | 1 | 法を指定した加算演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases}0 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[2] = 0\\ (\boldsymbol{\mu}_{\mathbf{s}}[0] + \boldsymbol{\mu}_{\mathbf{s}}[1]) \bmod \boldsymbol{\mu}_{\mathbf{s}}[2] & \text{otherwise}\end{cases}`$ この演算の中間計算には $`2^{256}`$ を法とする剰余を適用しない。 |
| 0x09 | MULMOD | 3 | 1 | 法を指定した乗算演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases}0 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[2] = 0\\ (\boldsymbol{\mu}_{\mathbf{s}}[0] \times \boldsymbol{\mu}_{\mathbf{s}}[1]) \bmod \boldsymbol{\mu}_{\mathbf{s}}[2] & \text{otherwise}\end{cases}`$ この演算の中間計算には $`2^{256}`$ を法とする剰余を適用しない。 |
| 0x0a | EXP | 2 | 1 | べき乗演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathbf{s}}[0] ^ {\boldsymbol{\mu}_{\mathbf{s}}[1] }`$ |
| 0x0b | SIGNEXTEND | 2 | 1 | 2の補数表現の符号付き整数を符号拡張する。 $`\forall i \in [0..255]: \boldsymbol{\mu}'_{\mathbf{s}}[0]_{\mathrm{i}} \equiv \begin{cases} \boldsymbol{\mu}_{\mathbf{s}}[1]_{\mathrm{t}} &\text{if} \quad i \leqslant t \quad \text{where} \; t = 256 - 8(\boldsymbol{\mu}_{\mathbf{s}}[0] + 1) \\ \boldsymbol{\mu}_{\mathbf{s}}[1]_{\mathrm{i}} &\text{otherwise} \end{cases}`$ |

$`\boldsymbol{\mu}_{\mathbf{s}}[x]_{\mathrm{i}}`$ は、 $`\boldsymbol{\mu}_{\mathbf{s}}[x]`$ の第 $`i`$ ビット（0から数える）を表す。

**0x10番台：比較とビット単位の論理演算**

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0x10 | LT | 2 | 1 | 小なり比較。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases} 1 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[0] < \boldsymbol{\mu}_{\mathbf{s}}[1] \\ 0 & \text{otherwise} \end{cases}`$ |
| 0x11 | GT | 2 | 1 | 大なり比較。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases} 1 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[0] > \boldsymbol{\mu}_{\mathbf{s}}[1] \\ 0 & \text{otherwise} \end{cases}`$ |
| 0x12 | SLT | 2 | 1 | 符号付き小なり比較。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases} 1 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[0] < \boldsymbol{\mu}_{\mathbf{s}}[1] \\ 0 & \text{otherwise} \end{cases}`$ ここでは、すべての値を2の補数表現の符号付き256ビット整数として扱う。 |
| 0x13 | SGT | 2 | 1 | 符号付き大なり比較。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases} 1 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[0] > \boldsymbol{\mu}_{\mathbf{s}}[1] \\ 0 & \text{otherwise} \end{cases}`$ ここでは、すべての値を2の補数表現の符号付き256ビット整数として扱う。 |
| 0x14 | EQ | 2 | 1 | 等値比較。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases} 1 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[0] = \boldsymbol{\mu}_{\mathbf{s}}[1] \\ 0 & \text{otherwise} \end{cases}`$ |
| 0x15 | ISZERO | 1 | 1 | 単純な否定演算子。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases} 1 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[0] = 0 \\ 0 & \text{otherwise} \end{cases}`$ |
| 0x16 | AND | 2 | 1 | ビット単位AND演算。 $`\forall i \in [0..255]: \boldsymbol{\mu}'_{\mathbf{s}}[0]_{\mathrm{i}} \equiv \boldsymbol{\mu}_{\mathbf{s}}[0]_{\mathrm{i}} \wedge \boldsymbol{\mu}_{\mathbf{s}}[1]_{\mathrm{i}}`$ |
| 0x17 | OR | 2 | 1 | ビット単位OR演算。 $`\forall i \in [0..255]: \boldsymbol{\mu}'_{\mathbf{s}}[0]_{\mathrm{i}} \equiv \boldsymbol{\mu}_{\mathbf{s}}[0]_{\mathrm{i}} \vee \boldsymbol{\mu}_{\mathbf{s}}[1]_{\mathrm{i}}`$ |
| 0x18 | XOR | 2 | 1 | ビット単位XOR演算。 $`\forall i \in [0..255]: \boldsymbol{\mu}'_{\mathbf{s}}[0]_{\mathrm{i}} \equiv \boldsymbol{\mu}_{\mathbf{s}}[0]_{\mathrm{i}} \oplus \boldsymbol{\mu}_{\mathbf{s}}[1]_{\mathrm{i}}`$ |
| 0x19 | NOT | 1 | 1 | ビット単位NOT演算。 $`\forall i \in [0..255]: \boldsymbol{\mu}'_{\mathbf{s}}[0]_{\mathrm{i}} \equiv \begin{cases} 1 & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[0]_{\mathrm{i}} = 0 \\ 0 & \text{otherwise} \end{cases}`$ |
| 0x1a | BYTE | 2 | 1 | ワードから1バイトを取り出す。 $`\forall i \in [0..255]: \boldsymbol{\mu}'_{\mathbf{s}}[0]_{\mathrm{i}} \equiv \begin{cases} \boldsymbol{\mu}_{\mathbf{s}}[1]_{(i - 248 + 8\boldsymbol{\mu}_{\mathbf{s}}[0])} & \text{if} \quad i \geq 248 \wedge \boldsymbol{\mu}_{\mathbf{s}}[0] < 32 \\ 0 & \text{otherwise} \end{cases}`$ 第Nバイトは左から数える（すなわちN=0はビッグエンディアンで最上位となる）。 |
| 0x1b | SHL | 2 | 1 | 左シフト演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv (\boldsymbol{\mu}_{\mathbf{s}}[1] \times 2^{\boldsymbol{\mu}_{\mathbf{s}}[0]}) \bmod 2^{256}`$ |
| 0x1c | SHR | 2 | 1 | 論理右シフト演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \lfloor \boldsymbol{\mu}_{\mathbf{s}}[1] \div 2^{\boldsymbol{\mu}_{\mathbf{s}}[0]} \rfloor`$ |
| 0x1d | SAR | 2 | 1 | 算術（符号付き）右シフト演算。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \lfloor \boldsymbol{\mu}_{\mathbf{s}}[1] \div 2^{\boldsymbol{\mu}_{\mathbf{s}}[0]} \rfloor`$ ここでは、 $`\boldsymbol{\mu}'_{\mathbf{s}}[0]`$ と $`\boldsymbol{\mu}_{\mathbf{s}}[1]`$ を2の補数表現の符号付き256ビット整数として扱い、 $`\boldsymbol{\mu}_{\mathbf{s}}[0]`$ は符号なしとして扱う。 |

**0x20番台：KECCAK256**

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0x20 | KECCAK256 | 2 | 1 | Keccak-256ハッシュを計算する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \mathtt{KEC}(\boldsymbol{\mu}_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[0] \dots (\boldsymbol{\mu}_{\mathbf{s}}[0] + \boldsymbol{\mu}_{\mathbf{s}}[1] - 1) ])`$ $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[0], \boldsymbol{\mu}_{\mathbf{s}}[1])`$ |

**0x30番台：環境情報**

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0x30 | ADDRESS | 0 | 1 | 現在実行中のアカウントのアドレスを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv I_{\mathrm{a}}`$ |
| 0x31 | BALANCE | 1 | 1 | 所与のアカウントの残高を取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases}\boldsymbol{\sigma}[\boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}]_{\mathrm{b}}& \text{if} \quad \boldsymbol{\sigma}[\boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}] \neq \varnothing\\0&\text{otherwise}\end{cases}`$ $`A'_{\mathbf{a}} \equiv A_{\mathbf{a}} \cup \{ \boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160} \}`$ |
| 0x32 | ORIGIN | 0 | 1 | 実行の起点となるアドレスを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv I_{\mathrm{o}}`$ これは元のトランザクションの送信者であり、空でない関連コードを持つアカウントには決してならない。 |
| 0x33 | CALLER | 0 | 1 | 呼出元アドレスを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv I_{\mathrm{s}}`$ これは、この実行に直接責任を持つアカウントのアドレスである。 |
| 0x34 | CALLVALUE | 0 | 1 | この実行を生じさせた命令またはトランザクションが預け入れた値を取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv I_{\mathrm{v}}`$ |
| 0x35 | CALLDATALOAD | 1 | 1 | 現在の環境の入力データを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv I_{\mathbf{d}}[ \boldsymbol{\mu}_{\mathbf{s}}[0] \dots (\boldsymbol{\mu}_{\mathbf{s}}[0] + 31) ] \quad \text{with} \quad I_{\mathbf{d}}[x] = 0 \quad \text{if} \quad x \geqslant \lVert I_{\mathbf{d}} \rVert`$ これは、メッセージ呼出し命令またはトランザクションで渡された入力データに関するものである。 |
| 0x36 | CALLDATASIZE | 0 | 1 | 現在の環境の入力データ・サイズを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \lVert I_{\mathbf{d}} \rVert`$ これは、メッセージ呼出し命令またはトランザクションで渡された入力データに関するものである。 |
| 0x37 | CALLDATACOPY | 3 | 0 | 現在の環境の入力データをメモリへコピーする。 $`\forall i \in \{ 0 \dots \boldsymbol{\mu}_{\mathbf{s}}[2] - 1\}: \boldsymbol{\mu}'_{\mathbf{m}}[\boldsymbol{\mu}_{\mathbf{s}}[0] + i ] \equiv \begin{cases} I_{\mathbf{d}}[\boldsymbol{\mu}_{\mathbf{s}}[1] + i] & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[1] + i < \lVert I_{\mathbf{d}} \rVert \\ 0 & \text{otherwise} \end{cases}`$ $`\boldsymbol{\mu}_{\mathbf{s}}[1] + i`$ の加算には $`2^{256}`$ を法とする剰余を適用しない。 $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[0], \boldsymbol{\mu}_{\mathbf{s}}[2])`$ これは、メッセージ呼出し命令またはトランザクションで渡された入力データに関するものである。 |
| 0x38 | CODESIZE | 0 | 1 | 現在の環境で実行中のコードのサイズを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \lVert I_{\mathbf{b}} \rVert`$ |
| 0x39 | CODECOPY | 3 | 0 | 現在の環境で実行中のコードをメモリへコピーする。 $`\forall i \in \{ 0 \dots \boldsymbol{\mu}_{\mathbf{s}}[2] - 1\}: \boldsymbol{\mu}'_{\mathbf{m}}[\boldsymbol{\mu}_{\mathbf{s}}[0] + i ] \equiv \begin{cases} I_{\mathbf{b}}[\boldsymbol{\mu}_{\mathbf{s}}[1] + i] & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[1] + i < \lVert I_{\mathbf{b}} \rVert \\ \text{STOP} & \text{otherwise} \end{cases}`$ $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[0], \boldsymbol{\mu}_{\mathbf{s}}[2])`$ $`\boldsymbol{\mu}_{\mathbf{s}}[1] + i`$ の加算には $`2^{256}`$ を法とする剰余を適用しない。 |
| 0x3a | GASPRICE | 0 | 1 | 現在の環境のgas価格を取得する。 これは[第6節](../chapters/06-transaction-execution.md#ch:transactions)で定義した*実効gas価格*である。 *London* ハードフォーク以降、この値はバリデータが受け取る額ではなく、単に送信者が支払う額を表すことに注意されたい。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv I_{\mathrm{p}}`$ |
| 0x3b | EXTCODESIZE | 1 | 1 | アカウントのコード・サイズを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases} \lVert \mathbf{b} \rVert & \text{if} \quad \boldsymbol{\sigma}[\boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}] \neq \varnothing \\ 0 & \text{otherwise} \end{cases}`$ ここで $`\mathtt{KEC}(\mathbf{b}) \equiv \boldsymbol{\sigma}[\boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}]_{\mathrm{c}}`$ である。 $`A'_{\mathbf{a}} \equiv A_{\mathbf{a}} \cup \{ \boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160} \}`$ |
| 0x3c | EXTCODECOPY | 4 | 0 | アカウントのコードをメモリへコピーする。 $`\forall i \in \{ 0 \dots \boldsymbol{\mu}_{\mathbf{s}}[3] - 1\}: \boldsymbol{\mu}'_{\mathbf{m}}[\boldsymbol{\mu}_{\mathbf{s}}[1] + i ] \equiv \begin{cases} \mathbf{b}[\boldsymbol{\mu}_{\mathbf{s}}[2] + i] & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[2] + i < \lVert \mathbf{b} \rVert \\ \text{STOP} & \text{otherwise} \end{cases}`$ ここで $`\mathtt{KEC}(\mathbf{b}) \equiv \boldsymbol{\sigma}[\boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}]_{\mathrm{c}}`$ である。 $`\boldsymbol{\sigma}[\boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}] = \varnothing`$ ならば $`\mathbf{b} \equiv ()`$ と仮定する。 $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[1], \boldsymbol{\mu}_{\mathbf{s}}[3])`$ $`\boldsymbol{\mu}_{\mathbf{s}}[2] + i`$ の加算には $`2^{256}`$ を法とする剰余を適用しない。 $`A'_{\mathbf{a}} \equiv A_{\mathbf{a}} \cup \{ \boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160} \}`$ |

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0x3d | RETURNDATASIZE | 0 | 1 | 現在の環境から行った直前の呼出しの出力データ・サイズを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \lVert \boldsymbol{\mu}_{\mathbf{o}} \rVert`$ |
| 0x3e | RETURNDATACOPY | 3 | 0 | 直前の呼出しの出力データをメモリへコピーする。 $`\forall i \in \{ 0 \dots \boldsymbol{\mu}_{\mathbf{s}}[2] - 1\}: \boldsymbol{\mu}'_{\mathbf{m}}[\boldsymbol{\mu}_{\mathbf{s}}[0] + i ] \equiv \begin{cases} \boldsymbol{\mu}_{\mathbf{o}}[\boldsymbol{\mu}_{\mathbf{s}}[1] + i] & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[1] + i < \lVert \boldsymbol{\mu}_{\mathbf{o}} \rVert \\ 0 & \text{otherwise} \end{cases}`$ $`\boldsymbol{\mu}_{\mathbf{s}}[1] + i`$ の加算には $`2^{256}`$ を法とする剰余を適用しない。 $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[0], \boldsymbol{\mu}_{\mathbf{s}}[2])`$ |
| 0x3f | EXTCODEHASH | 1 | 1 | アカウントのコードのハッシュを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \begin{cases} 0 & \text{if} \quad \mathtt{DEAD}(\boldsymbol{\sigma}, \boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}) \\ \boldsymbol{\sigma}[\boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}]_{\mathrm{c}} & \text{otherwise} \end{cases}`$ $`A'_{\mathbf{a}} \equiv A_{\mathbf{a}} \cup \{ \boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160} \}`$ |

**0x40番台：ブロック情報**

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0x40 | <span id="blockhash"></span>BLOCKHASH | 1 | 1 | 直近256個の完全なブロックのうち一つのハッシュを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv P(I_{\mathrm{H}_{\mathrm{p}}}, \boldsymbol{\mu}_{\mathbf{s}}[0], 0)`$ ここで $`P`$ は、最大経過ブロック数までの範囲にある特定番号のブロックのハッシュである。求めるブロック番号が現在のブロック番号以上である場合、または現在のブロックより256ブロック超前である場合、スタックには0が残される。 $`P(h, n, a) \equiv \begin{cases} 0 & \text{if} \quad n > H_{\mathrm{i}} \vee a = 256 \vee h = 0 \\ h & \text{if} \quad n = H_{\mathrm{i}} \\ P(H_{\mathrm{p}}, n, a + 1) & \text{otherwise} \end{cases}`$ また、 $`h`$ がゼロ（ジェネシス・ブロックの親ハッシュの場合）でない限り、ヘッダ $`H`$ はそのハッシュ $`h`$ から特定できると仮定する。 |
| 0x41 | COINBASE | 0 | 1 | 現在のブロックの受益者アドレスを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv {I_{\mathrm{H}}}_{\mathrm{c}}`$ |
| 0x42 | TIMESTAMP | 0 | 1 | 現在のブロックのタイムスタンプを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv {I_{\mathrm{H}}}_{\mathrm{s}}`$ |
| 0x43 | NUMBER | 0 | 1 | 現在のブロック番号を取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv {I_{\mathrm{H}}}_{\mathrm{i}}`$ |
| 0x44 | PREVRANDAO | 0 | 1 | 直前のブロックを処理した後のビーコン状態における最新のRANDAO mixを取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv {I_{\mathrm{H}}}_{\mathrm{a}}`$ |
| 0x45 | GASLIMIT | 0 | 1 | 現在のブロックのgas上限を取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv {I_{\mathrm{H}}}_{\mathrm{l}}`$ |
| 0x46 | CHAINID | 0 | 1 | [チェーンID](../chapters/02-blockchain-paradigm.md#chain_id)を取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \beta`$ |
| 0x47 | SELFBALANCE | 0 | 1 | 現在実行中のアカウントの残高を取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}}`$ |
| 0x48 | BASEFEE | 0 | 1 | 現在のブロックの基本手数料を取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv {I_{\mathrm{H}}}_{\mathrm{f}}`$ |

**0x50番台：スタック、メモリ、ストレージ、制御フローの演算**

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0x50 | POP | 1 | 0 | スタックから項目を取り除く。 |
| 0x51 | MLOAD | 1 | 1 | メモリからワードを読み込む。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathbf{m}}[\boldsymbol{\mu}_{\mathbf{s}}[0] \dots (\boldsymbol{\mu}_{\mathbf{s}}[0] + 31) ]`$ $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv \max(\boldsymbol{\mu}_{\mathrm{i}}, \left\lceil (\boldsymbol{\mu}_{\mathbf{s}}[0] + 32) \div 32 \right\rceil)`$ $`\boldsymbol{\mu}'_{\mathrm{i}}`$ の計算における加算には $`2^{256}`$ を法とする剰余を適用しない。 |
| 0x52 | MSTORE | 2 | 0 | ワードをメモリへ保存する。 $`\boldsymbol{\mu}'_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[0] \dots (\boldsymbol{\mu}_{\mathbf{s}}[0] + 31) ] \equiv \boldsymbol{\mu}_{\mathbf{s}}[1]`$ $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv \max(\boldsymbol{\mu}_{\mathrm{i}}, \left\lceil (\boldsymbol{\mu}_{\mathbf{s}}[0] + 32) \div 32 \right\rceil)`$ $`\boldsymbol{\mu}'_{\mathrm{i}}`$ の計算における加算には $`2^{256}`$ を法とする剰余を適用しない。 |
| 0x53 | MSTORE8 | 2 | 0 | バイトをメモリへ保存する。 $`\boldsymbol{\mu}'_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[0] ] \equiv (\boldsymbol{\mu}_{\mathbf{s}}[1] \bmod 256)`$ $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv \max(\boldsymbol{\mu}_{\mathrm{i}}, \left\lceil (\boldsymbol{\mu}_{\mathbf{s}}[0] + 1) \div 32 \right\rceil)`$ $`\boldsymbol{\mu}'_{\mathrm{i}}`$ の計算における加算には $`2^{256}`$ を法とする剰余を適用しない。 |
| 0x54 | SLOAD | 1 | 1 | ストレージからワードを読み込む。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathbf{s}}[\boldsymbol{\mu}_{\mathbf{s}}[0]]`$ $`A'_{\mathbf{K}} \equiv A_{\mathbf{K}} \cup \{(I_{\mathrm{a}}, \boldsymbol{\mu}_{\mathbf{s}}[0])\}`$ $`C_{\text{SLOAD}}(\boldsymbol{\mu}, A, I) \equiv \begin{cases} G_{\mathrm{warmaccess}} & \text{if} \quad (I_{\mathrm{a}}, \boldsymbol{\mu}_{\mathbf{s}}[0]) \in A_{\mathbf{K}} \\ G_{\mathrm{coldsload}} & \text{otherwise} \end{cases}`$ |
| 0x55 | <span id="SSTORE"></span><span id="C__SSTORE"></span>SSTORE | 2 | 0 | ワードをストレージへ保存する。 $`\boldsymbol{\sigma}'[I_{\mathrm{a}}]_{\mathbf{s}}[ \boldsymbol{\mu}_{\mathbf{s}}[0] ] \equiv \boldsymbol{\mu}_{\mathbf{s}}[1]`$ $`A'_{\mathbf{K}} \equiv A_{\mathbf{K}} \cup \{(I_{\mathrm{a}}, \boldsymbol{\mu}_{\mathbf{s}}[0])\}`$ $`C_{\text{SSTORE}}(\boldsymbol{\sigma}, \boldsymbol{\mu})`$ と $`A'_{\mathrm{r}}`$ は、EIP-2200によって次のように規定される。 チェックポイント（「元の」）状態 $`\boldsymbol{\sigma}_0`$ は、現在のトランザクションがリバートした場合の状態であることを改めて述べておく。 $`v_0 = \boldsymbol{\sigma}_0[I_{\mathrm{a}}]_{\mathbf{s}}[\boldsymbol{\mu}_{\mathbf{s}}[0]]`$ をストレージ・スロットの元の値とする。 $`v = \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathbf{s}}[\boldsymbol{\mu}_{\mathbf{s}}[0]]`$ を現在値とする。 $`v' = \boldsymbol{\mu}_{\mathbf{s}}[1]`$ を新しい値とする。 このとき、 $`\!\begin{aligned} C_{\text{SSTORE}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) &\equiv \begin{cases} 0 & \text{if} \quad (I_{\mathrm{a}}, \boldsymbol{\mu}_{\mathbf{s}}[0]) \in A_{\mathbf{K}} \\ G_{\mathrm{coldsload}} & \text{otherwise} \\ \end{cases} \\ &+ \begin{cases} G_{\mathrm{warmaccess}} & \text{if} \quad v = v' \; \vee \; v_0 \neq v \\ G_{\mathrm{sset}} & \text{if} \quad v \neq v' \; \wedge \; v_0 = v \; \wedge \; v_0 = 0 \\ G_{\mathrm{sreset}} & \text{if} \quad v \neq v' \; \wedge \; v_0 = v \; \wedge \; v_0 \neq 0 \\ \end{cases} \end{aligned}`$ $`A'_{\mathrm{r}} \equiv A_{\mathrm{r}} + \begin{cases} R_{\mathrm{sclear}} & \text{if} \quad v \neq v' \; \wedge \; v_0 = v \; \wedge \; v' = 0 \\ r_{\text{dirtyclear}} + r_{\text{dirtyreset}} & \text{if} \quad v \neq v' \; \wedge \; v_0 \neq v \\ 0 & \text{otherwise} \\ \end{cases}`$ ここで、 $`r_{\text{dirtyclear}} \equiv \begin{cases} -R_{\mathrm{sclear}} & \text{if} \quad v_0 \neq 0 \; \wedge \; v = 0 \\ R_{\mathrm{sclear}} & \text{if} \quad v_0 \neq 0 \; \wedge \; v' = 0 \\ 0 & \text{otherwise} \\ \end{cases}`$ $`r_{\text{dirtyreset}} \equiv \begin{cases} G_{\mathrm{sset}} - G_{\mathrm{warmaccess}} & \text{if} \quad v_0 = v' \; \wedge \; v_0 = 0 \\ G_{\mathrm{sreset}} - G_{\mathrm{warmaccess}} & \text{if} \quad v_0 = v' \; \wedge \; v_0 \neq 0 \\ 0 & \text{otherwise} \\ \end{cases}`$ |
| 0x56 | JUMP | 1 | 0 | プログラム・カウンタを変更する。 $`J_{\text{JUMP}}(\boldsymbol{\mu}) \equiv \boldsymbol{\mu}_{\mathbf{s}}[0]`$ これは当該値を $`\boldsymbol{\mu}_{\mathrm{pc}}`$ へ書き込む効果を持つ。[第9節](../chapters/09-execution-model.md#ch:model)を参照されたい。 |
| 0x57 | JUMPI | 2 | 0 | 条件付きでプログラム・カウンタを変更する。 $`J_{\text{JUMPI}}(\boldsymbol{\mu}) \equiv \begin{cases} \boldsymbol{\mu}_{\mathbf{s}}[0] & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[1] \neq 0 \\ \boldsymbol{\mu}_{\mathrm{pc}} + 1 & \text{otherwise} \end{cases}`$ これは当該値を $`\boldsymbol{\mu}_{\mathrm{pc}}`$ へ書き込む効果を持つ。[第9節](../chapters/09-execution-model.md#ch:model)を参照されたい。 |
| 0x58 | PC | 0 | 1 | この命令に対応する増分を行う*前*のプログラム・カウンタ値を取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathrm{pc}}`$ |

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0x59 | MSIZE | 0 | 1 | アクティブ・メモリのサイズをバイト単位で取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv 32\boldsymbol{\mu}_{\mathrm{i}}`$ |
| 0x5a | GAS | 0 | 1 | この命令のコストに対応する減少を含め、利用可能なgas量を取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathrm{g}}`$ |
| 0x5b | JUMPDEST | 0 | 0 | ジャンプの妥当な行先を示す。 この演算は、実行中のマシン状態に影響を与えない。 |

**0x5f、0x60番台、0x70番台：プッシュ演算**

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0x5f | PUSH0 | 0 | 1 | スタックへ0を置く。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv 0`$ |
| 0x60 | PUSH1 | 0 | 1 | 1バイトの項目をスタックへ置く。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv c(\boldsymbol{\mu}_{\mathrm{pc}} + 1)`$ $`\text{where} \quad c(x) \equiv \begin{cases} I_{\mathbf{b}}[x] & \text{if} \quad x < \lVert I_{\mathbf{b}} \rVert \\ 0 & \text{otherwise} \end{cases}`$ バイトはプログラム・コードのバイト配列から順に読み込む。 関数 $`c`$ は、境界を越えたバイトの既定値がゼロとなることを保証する。 バイトは右寄せされる（ビッグエンディアンで最下位位置を占める）。 |
| 0x61 | PUSH2 | 0 | 1 | 2バイトの項目をスタックへ置く。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{c}\big( (\boldsymbol{\mu}_{\mathrm{pc}} + 1) \dots (\boldsymbol{\mu}_{\mathrm{pc}} + 2) \big)`$ ここで $`\boldsymbol{c}(\boldsymbol{x}) \equiv (c(\boldsymbol{x}_0), ..., c(\boldsymbol{x}_{\lVert x \rVert -1}))`$ であり、 $`c`$ は上記の定義による。 バイトは右寄せされる（ビッグエンディアンで最下位位置を占める）。 |
| ⋮ | ⋮ | ⋮ | ⋮ | ⋮ |
| 0x7f | PUSH32 | 0 | 1 | 32バイト（完全な1ワード）の項目をスタックへ置く。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{c}\big((\boldsymbol{\mu}_{\mathrm{pc}} + 1) \dots (\boldsymbol{\mu}_{\mathrm{pc}} + 32) \big)`$ ここで $`\boldsymbol{c}`$ は上記の定義による。 バイトは右寄せされる（ビッグエンディアンで最下位位置を占める）。 |

**0x80番台：複製演算**

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0x80 | DUP1 | 1 | 2 | スタックの第1項目を複製する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathbf{s}}[0]`$ |
| 0x81 | DUP2 | 2 | 3 | スタックの第2項目を複製する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathbf{s}}[1]`$ |
| ⋮ | ⋮ | ⋮ | ⋮ | ⋮ |
| 0x8f | DUP16 | 16 | 17 | スタックの第16項目を複製する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathbf{s}}[15]`$ |

**0x90番台：交換演算**

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0x90 | SWAP1 | 2 | 2 | スタックの第1項目と第2項目を交換する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathbf{s}}[1]`$ $`\boldsymbol{\mu}'_{\mathbf{s}}[1] \equiv \boldsymbol{\mu}_{\mathbf{s}}[0]`$ |
| 0x91 | SWAP2 | 3 | 3 | スタックの第1項目と第3項目を交換する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathbf{s}}[2]`$ $`\boldsymbol{\mu}'_{\mathbf{s}}[2] \equiv \boldsymbol{\mu}_{\mathbf{s}}[0]`$ |
| ⋮ | ⋮ | ⋮ | ⋮ | ⋮ |
| 0x9f | SWAP16 | 17 | 17 | スタックの第1項目と第17項目を交換する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \boldsymbol{\mu}_{\mathbf{s}}[16]`$ $`\boldsymbol{\mu}'_{\mathbf{s}}[16] \equiv \boldsymbol{\mu}_{\mathbf{s}}[0]`$ |

**0xa0番台：ログ演算**

すべてのログ演算について、状態変更はサブ状態のログ列へログ・エントリを追加することである。

<!-- 原文では無番号の表示式 -->

```math
A'_{\mathbf{l}} \equiv A_{\mathbf{l}} \cdot (I_{\mathrm{a}}, \mathbf{t}, \boldsymbol{\mu}_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[0] \dots (\boldsymbol{\mu}_{\mathbf{s}}[0] + \boldsymbol{\mu}_{\mathbf{s}}[1] - 1) ])
```

また、メモリ使用量カウンタを更新する。

<!-- 原文では無番号の表示式 -->

```math
\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[0], \boldsymbol{\mu}_{\mathbf{s}}[1])
```

エントリのトピック列 $`\mathbf{t}`$ は、次のとおり演算によって異なる。

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0xa0 | LOG0 | 2 | 0 | トピックなしのログ・レコードを追加する。 $`\mathbf{t} \equiv ()`$ |
| 0xa1 | LOG1 | 3 | 0 | トピック一つのログ・レコードを追加する。 $`\mathbf{t} \equiv (\boldsymbol{\mu}_{\mathbf{s}}[2])`$ |
| ⋮ | ⋮ | ⋮ | ⋮ | ⋮ |
| 0xa4 | LOG4 | 6 | 0 | トピック四つのログ・レコードを追加する。 $`\mathbf{t} \equiv (\boldsymbol{\mu}_{\mathbf{s}}[2], \boldsymbol{\mu}_{\mathbf{s}}[3], \boldsymbol{\mu}_{\mathbf{s}}[4], \boldsymbol{\mu}_{\mathbf{s}}[5])`$ |

**0xf0番台：システム演算**

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0xf0 | CREATE | 3 | 1 | 関連コードを持つ新しいアカウントを作成する。 $`\mathbf{i} \equiv \boldsymbol{\mu}_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[1] \dots (\boldsymbol{\mu}_{\mathbf{s}}[1] + \boldsymbol{\mu}_{\mathbf{s}}[2] - 1) ]`$ $`\zeta \equiv \varnothing`$ $`(\boldsymbol{\sigma}', g', A', z, \mathbf{o}) \equiv \begin{cases} \Lambda(\boldsymbol{\sigma}^{*}, A, I_{\mathrm{a}}, I_{\mathrm{o}}, L(\boldsymbol{\mu}_{\mathrm{g}}), I_{\mathrm{p}}, \boldsymbol{\mu}_{\mathbf{s}}[0], \mathbf{i}, I_{\mathrm{e}} + 1, \zeta, I_{\mathrm{w}}) & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[0] \leqslant \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}} \; \wedge \\ \quad &\; I_{\mathrm{e}} < 1024 \wedge \lVert \mathbf{i} \rVert \leqslant 49152\\ \big(\boldsymbol{\sigma}, L(\boldsymbol{\mu}_{\mathrm{g}}), A, 0, () \big) & \text{otherwise} \end{cases}`$ $`\boldsymbol{\sigma}^{*} \equiv \boldsymbol{\sigma} \quad \text{except} \quad \boldsymbol{\sigma}^{*}[I_{\mathrm{a}}]_{\mathrm{n}} = \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{n}} + 1`$ $`\boldsymbol{\mu}'_{\mathrm{g}} \equiv \boldsymbol{\mu}_{\mathrm{g}} - L(\boldsymbol{\mu}_{\mathrm{g}}) + g'`$ $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv x`$ $`z = 0`$ 、すなわち[コントラクト作成処理が失敗](../chapters/07-contract-creation.md#contract_creation_result)した場合、 または $`\lVert \mathbf{i} \rVert > 49152`$ （初期化コードが49152バイトより長い）、 または $`I_{\mathrm{e}} = 1024`$ （最大呼出し深度の上限に達した）、 または $`\boldsymbol{\mu}_{\mathbf{s}}[0] > \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}}`$ （呼出元の残高が値の移転を満たすには不足している）ならば $`x=0`$ とする。 それ以外では、 $`x=\mathtt{ADDR}(I_{\mathrm{a}}, \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{n}}, \zeta, \mathbf{i} )`$ 、すなわち新たに作成したアカウントのアドレス（[95](../chapters/07-contract-creation.md#eq:new-address)）とする。 $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[1], \boldsymbol{\mu}_{\mathbf{s}}[2])`$ $`\boldsymbol{\mu}'_{\mathbf{o}} \equiv \begin{cases} () & \text{if} \quad z = 1 \\ \mathbf{o} & \text{otherwise} \end{cases}`$ したがってオペランドの順序は、値、入力オフセット、入力サイズである。 |
| 0xf1 | CALL | 7 | 1 | アカウントへメッセージ呼出しを行う。 $`\mathbf{i} \equiv \boldsymbol{\mu}_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[3] \dots (\boldsymbol{\mu}_{\mathbf{s}}[3] + \boldsymbol{\mu}_{\mathbf{s}}[4] - 1) ]`$ $`(\boldsymbol{\sigma}', g', A', x, \mathbf{o}) \equiv \begin{cases} \begin{array}{l}\Theta(\boldsymbol{\sigma}, A^{*}, I_{\mathrm{a}}, I_{\mathrm{o}}, t, t, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A),\\ \quad I_{\mathrm{p}}, \boldsymbol{\mu}_{\mathbf{s}}[2], \boldsymbol{\mu}_{\mathbf{s}}[2], \mathbf{i}, I_{\mathrm{e}} + 1, I_{\mathrm{w}})\end{array} & \begin{array}{l}\text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[2] \leqslant \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}} \;\wedge \\ \quad\quad I_{\mathrm{e}} < 1024\end{array}\\ (\boldsymbol{\sigma}, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A), A^{*}, 0, ()) & \text{otherwise} \end{cases}`$ $`n \equiv \min(\{ \boldsymbol{\mu}_{\mathbf{s}}[6], \lVert \mathbf{o} \rVert\})`$ $`\boldsymbol{\mu}'_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[5] \dots (\boldsymbol{\mu}_{\mathbf{s}}[5] + n - 1) ] = \mathbf{o}[0 \dots (n - 1)]`$ $`\boldsymbol{\mu}'_{\mathbf{o}} = \mathbf{o}`$ $`\boldsymbol{\mu}'_{\mathrm{g}} \equiv \boldsymbol{\mu}_{\mathrm{g}} - C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A) + g'`$ $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv x`$ $`A^{*} \equiv A \quad \text{except} \quad A^{*}_{\mathbf{a}} \equiv A_{\mathbf{a}} \cup \{t\}`$ $`t \equiv \boldsymbol{\mu}_{\mathbf{s}}[1] \bmod 2^{160}`$ $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[3], \boldsymbol{\mu}_{\mathbf{s}}[4]), \boldsymbol{\mu}_{\mathbf{s}}[5], \boldsymbol{\mu}_{\mathbf{s}}[6])`$ [この演算のコード実行が失敗](../chapters/08-message-call.md#code_execution_result)した場合、または $`\boldsymbol{\mu}_{\mathbf{s}}[2] > \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}}`$ （資金不足）、または $`I_{\mathrm{e}} = 1024`$ （呼出し深度の上限に到達）の場合は $`x=0`$ とし、 それ以外では $`x=1`$ とする。 したがってオペランドの順序は、gas、宛先、値、入力オフセット、入力サイズ、出力オフセット、出力サイズである。 $`C_{\text{CALL}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) \equiv C_{\text{GASCAP}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) + C_{\text{EXTRA}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A)`$ $`C_{\text{CALLGAS}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) \equiv \begin{cases} C_{\text{GASCAP}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) + G_{\mathrm{callstipend}} & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[2] \neq 0 \\ C_{\text{GASCAP}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) & \text{otherwise} \end{cases}`$ $`C_{\text{GASCAP}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) \equiv \begin{cases} \min\{ L(\boldsymbol{\mu}_{\mathrm{g}} - C_{\text{EXTRA}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A)), \boldsymbol{\mu}_{\mathbf{s}}[0] \} & \text{if} \quad \boldsymbol{\mu}_{\mathrm{g}} \ge C_{\text{EXTRA}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A)\\ \boldsymbol{\mu}_{\mathbf{s}}[0] & \text{otherwise} \end{cases}`$ $`C_{\text{EXTRA}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) \equiv C_{\mathrm{aaccess}}(t, A) + C_{\text{XFER}}(\boldsymbol{\mu}) + C_{\text{NEW}}(\boldsymbol{\sigma}, \boldsymbol{\mu})`$ $`C_{\text{XFER}}(\boldsymbol{\mu}) \equiv \begin{cases} G_{\mathrm{callvalue}} & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[2] \neq 0 \\ 0 & \text{otherwise} \end{cases}`$ $`C_{\text{NEW}}(\boldsymbol{\sigma}, \boldsymbol{\mu}) \equiv \begin{cases} G_{\mathrm{newaccount}} & \text{if} \quad \mathtt{DEAD}(\boldsymbol{\sigma}, t) \wedge \boldsymbol{\mu}_{\mathbf{s}}[2] \neq 0 \\ 0 & \text{otherwise} \end{cases}`$ |
| 0xf2 | CALLCODE | 7 | 1 | 別のアカウントのコードを用いて、このアカウントへメッセージ呼出しを行う。 次の点を除き、CALLと厳密に等価である。 $`(\boldsymbol{\sigma}', g', A', x, \mathbf{o}) \equiv \begin{cases}\begin{array}{l}\Theta(\boldsymbol{\sigma}, A^{*}, I_{\mathrm{a}}, I_{\mathrm{o}}, I_{\mathrm{a}}, t, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A), \\ \quad I_{\mathrm{p}}, \boldsymbol{\mu}_{\mathbf{s}}[2], \boldsymbol{\mu}_{\mathbf{s}}[2], \mathbf{i}, I_{\mathrm{e}} + 1, I_{\mathrm{w}})\end{array} & \begin{array}{l}\text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[2] \leqslant \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}} \;\wedge\\ \quad\quad{}I_{\mathrm{e}} < 1024\end{array} \\ (\boldsymbol{\sigma}, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A), A^{*}, 0, ()) & \text{otherwise} \end{cases}`$ 呼出し $`\Theta`$ の第4引数が、（CALLの場合の）スタック第2値 $`\boldsymbol{\mu}_{\mathbf{s}}[1]`$ から現在のアドレス $`I_{\mathrm{a}}`$ へ変更されていることに注意されたい。これは、受信者が実際には現在と同じアカウントであり、コードだけが置き換えられることを意味する。 |
| 0xf3 | <span id="RETURN"></span>RETURN | 2 | 0 | 出力データを返して実行を停止する。 $`H_{\text{RETURN}}(\boldsymbol{\mu}) \equiv \boldsymbol{\mu}_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[0] \dots ( \boldsymbol{\mu}_{\mathbf{s}}[0] + \boldsymbol{\mu}_{\mathbf{s}}[1] - 1 ) ]`$ これは、出力を定義したうえで、この地点で実行を停止する効果を持つ。 [第9節](../chapters/09-execution-model.md#ch:model)を参照されたい。 $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[0], \boldsymbol{\mu}_{\mathbf{s}}[1])`$ |

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0xf4 | DELEGATECALL | 6 | 1 | 現在の*送信者*と*値*を維持しつつ、別のアカウントのコードを用いて、このアカウントへメッセージ呼出しを行う。 CALLと比べ、DELEGATECALLは引数が一つ少ない。省略する引数は $`\boldsymbol{\mu}_{\mathbf{s}}[2]`$ である。そのため、CALLの定義にある $`\boldsymbol{\mu}_{\mathbf{s}}[3]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[4]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[5]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[6]`$ は、それぞれ $`\boldsymbol{\mu}_{\mathbf{s}}[2]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[3]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[4]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[5]`$ に置き換える。それ以外では、次の点を除きCALLと等価である。 $`(\boldsymbol{\sigma}', g', A', x, \mathbf{o}) \equiv \begin{cases}\begin{array}{l}\Theta(\boldsymbol{\sigma}, A^{*}, I_{\mathrm{s}}, I_{\mathrm{o}}, I_{\mathrm{a}}, t, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A), \\\quad I_{\mathrm{p}}, 0, I_{\mathrm{v}}, \mathbf{i}, I_{\mathrm{e}} + 1, I_{\mathrm{w}})\end{array} & \text{if} \quad I_{\mathrm{e}} < 1024 \\ (\boldsymbol{\sigma}, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A), A^{*}, 0, ()) & \text{otherwise} \end{cases}`$ 呼出し $`\Theta`$ の第4引数に加え、第2引数および第9引数も変更されていることに注意されたい。 これは、受信者が実際には現在と同じアカウントであり、コードだけが置き換えられ、かつ文脈がほぼ完全に同一であることを意味する。 |
| 0xf5 | <span id="create2"></span>CREATE2 | 4 | 1 | 関連コードを持つ新しいアカウントを作成する。 次の点を除き、CREATEと厳密に等価である。 saltは $`\zeta \equiv \boldsymbol{\mu}_{\mathbf{s}}[3]`$ である。 |
| 0xfa | STATICCALL | 6 | 1 | アカウントへ静的メッセージ呼出しを行う。 次の点を除き、CALLと厳密に等価である。 引数 $`\boldsymbol{\mu}_{\mathbf{s}}[2]`$ を $`0`$ に置き換える。 後続の引数 $`\boldsymbol{\mu}_{\mathbf{s}}[3]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[4]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[5]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[6]`$ は、それぞれ $`\boldsymbol{\mu}_{\mathbf{s}}[2]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[3]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[4]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[5]`$ に置き換える。 $`\Theta`$ の最後の引数は $`\bot`$ である。 |
| 0xfd | <span id="REVERT"></span>REVERT | 2 | 0 | 状態変更をリバートしつつ、データと残存gasを返して実行を停止する。 $`H_{\text{RETURN}}(\boldsymbol{\mu}) \equiv \boldsymbol{\mu}_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[0] \dots ( \boldsymbol{\mu}_{\mathbf{s}}[0] + \boldsymbol{\mu}_{\mathbf{s}}[1] - 1 ) ]`$ この演算の効果は（[152](../chapters/09-execution-model.md#eq:X-def)）で記述する。 gasの計算にはメモリ拡張関数を用いる。 $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[0], \boldsymbol{\mu}_{\mathbf{s}}[1])`$ |
| 0xfe | INVALID | $`\varnothing`$ | $`\varnothing`$ | 無効と指定された命令。 |
| 0xff | SELFDESTRUCT | 1 | 0 | 実行を停止し、後で削除するアカウントとして登録する。*Shanghai* 更新以降、このオペコードは非推奨とされていることに注意されたい。 今後の更新で、その振る舞いに破壊的変更が加えられる可能性がある。 $`A'_{\mathbf{s}} \equiv A_{\mathbf{s}} \cup \{ I_{\mathrm{a}} \}`$ $`A'_{\mathbf{a}} \equiv A_{\mathbf{a}} \cup \{ r \}`$ $`\boldsymbol{\sigma}'[r] \equiv \begin{cases} \varnothing &\text{if}\quad \boldsymbol{\sigma}[r] = \varnothing\ \wedge\ \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}} = 0\\ (\boldsymbol{\sigma}[r]_{\mathrm{n}}, \boldsymbol{\sigma}[r]_{\mathrm{b}} + \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}}, \boldsymbol{\sigma}[r]_{\mathbf{s}}, \boldsymbol{\sigma}[r]_{\mathrm{c}}) & \text{if}\quad r \neq I_{\mathrm{a}} \\ (\boldsymbol{\sigma}[r]_{\mathrm{n}}, 0, \boldsymbol{\sigma}[r]_{\mathbf{s}}, \boldsymbol{\sigma}[r]_{\mathrm{c}}) & \text{otherwise} \end{cases}`$ ここで $`r = \boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}`$ である。 $`\boldsymbol{\sigma}'[I_{\mathrm{a}}]_{\mathrm{b}} = 0`$ $`\begin{aligned} C_{\text{SELFDESTRUCT}}(\boldsymbol{\sigma}, \boldsymbol{\mu}) &\equiv G_{\mathrm{selfdestruct}} + \begin{cases} 0 & \text{if}\quad r \in A_{\mathbf{a}}\\ G_{\mathrm{coldaccountaccess}} & \text{otherwise} \end{cases}\\ &+ \begin{cases} G_{\mathrm{newaccount}} & \text{if}\quad \mathtt{DEAD}(\boldsymbol{\sigma}, r) \wedge \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}} \neq 0 \\ 0 & \text{otherwise} \end{cases} \end{aligned}`$ |

<span id="tnref-11"></span>[訳注11](../translation-notes.md#tn-11)
