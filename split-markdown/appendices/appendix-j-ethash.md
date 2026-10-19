[分割版目次](../README.md) | [前へ](appendix-i-genesis-block.md) | [次へ](appendix-k-anomalies.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="app:ethash"></span>

# 付録J. Ethash

## J.1. 非推奨化

本節は歴史的理由から残されているが、*Paris* ハードフォーク以降、Ethashアルゴリズムは合意形成に使用されていない。

## J.2. 定義

次の定義を用いる。

| 名前 | 値 | 説明 |
| --- | --- | --- |
| $`J_{\mathrm{wordbytes}}`$ | 4 | 1ワードのバイト数。 |
| $`J_{\mathrm{datasetinit}}`$ | $`2^{30}`$ | ジェネシス時点のデータセットのバイト数。 |
| $`J_{\mathrm{datasetgrowth}}`$ | $`2^{23}`$ | エポックごとのデータセット増加量。 |
| $`J_{\mathrm{cacheinit}}`$ | $`2^{24}`$ | ジェネシス時点のキャッシュのバイト数。 |
| $`J_{\mathrm{cachegrowth}}`$ | $`2^{17}`$ | エポックごとのキャッシュ増加量。 |
| $`J_{\mathrm{epoch}}`$ | 30000 | エポック当たりのブロック数。 |
| $`J_{\mathrm{mixbytes}}`$ | 128 | mixの長さ（バイト単位）。 |
| $`J_{\mathrm{hashbytes}}`$ | 64 | ハッシュ長（バイト単位）。 |
| $`J_{\mathrm{parents}}`$ | 256 | データセット要素ごとの親の数。 |
| $`J_{\mathrm{cacherounds}}`$ | 3 | キャッシュ生成のラウンド数。 |
| $`J_{\mathrm{accesses}}`$ | 64 | hashimotoループにおけるアクセス回数。 |

## J.3. データセットとキャッシュのサイズ

Ethashのキャッシュ $`\mathbf{c} \in \mathbb{B}`$ とデータセット $`\mathbf{d} \in \mathbb{B}`$ のサイズはエポックに依存し、エポックはブロック番号に依存する。

<span id="eq-334"></span>

```math
E_{\mathrm{epoch}}(H_{\mathrm{i}}) = \left\lfloor\frac{H_{\mathrm{i}}}{J_{\mathrm{epoch}}}\right\rfloor \qquad \text{(334)}
```

エポックごとに、データセットのサイズは $`J_{\mathrm{datasetgrowth}}`$ バイト、キャッシュのサイズは $`J_{\mathrm{cachegrowth}}`$ バイト増加する。規則性による周期的挙動を避けるため、サイズは素数でなければならない。そのため、データセットについては $`J_{\mathrm{mixbytes}}`$ の倍数だけ、キャッシュについては $`J_{\mathrm{hashbytes}}`$ の倍数だけサイズを減少させる。データセットのサイズを $`d_{\mathrm{size}} = \lVert \mathbf{d} \rVert`$ とする。これは次式で計算される。

<span id="eq-335"></span>

```math
d_{\mathrm{size}} = E_{\mathrm{prime}}(J_{\mathrm{datasetinit}} + J_{\mathrm{datasetgrowth}} \cdot E_{\mathrm{epoch}} - J_{\mathrm{mixbytes}}, J_{\mathrm{mixbytes}}) \qquad \text{(335)}
```

キャッシュのサイズ $`c_{\mathrm{size}}`$ は次式で計算される。

<span id="eq-336"></span>

```math
c_{\mathrm{size}} = E_{\mathrm{prime}}(J_{\mathrm{cacheinit}} + J_{\mathrm{cachegrowth}} \cdot E_{\mathrm{epoch}} - J_{\mathrm{hashbytes}}, J_{\mathrm{hashbytes}}) \qquad \text{(336)}
```

<span id="eq-337"></span>

```math
E_{\mathrm{prime}}(x, y) = \begin{cases}
x & \text{if} \quad x / y \in \mathbb{N} \\
E_{\mathrm{prime}}(x - 2 \cdot y, y) & \text{otherwise}
\end{cases} \qquad \text{(337)}
```

<span id="tnref-12"></span>[訳注12](../translation-notes.md#tn-12)

## J.4. データセットの生成

データセットを生成するには、バイト配列であるキャッシュ $`\mathbf{c}`$ が必要である。これはキャッシュ・サイズ $`c_{\mathrm{size}}`$ とシード・ハッシュ $`\mathbf{s} \in \mathbb{B}_{32}`$ に依存する。

### J.4.1. シード・ハッシュ

シード・ハッシュはエポックごとに異なる。最初のエポックでは、32バイトのゼロ列のKeccak-256ハッシュである。それ以外の各エポックでは、常に直前のシード・ハッシュのKeccak-256ハッシュとなる。

<span id="eq-338"></span>

```math
\mathbf{s} = C_{\mathrm{seedhash}}(H_{\mathrm{i}}) \qquad \text{(338)}
```

<span id="eq-339"></span>

```math
C_{\mathrm{seedhash}}(H_{\mathrm{i}}) = \begin{cases}
\mathbf{0}_{32} & \text{if} \quad E_{\mathrm{epoch}}(H_{\mathrm{i}}) = 0 \quad  \\
\texttt{KEC}(C_{\mathrm{seedhash}}(H_{\mathrm{i}} - J_{\mathrm{epoch}})) & \text{otherwise}
\end{cases} \qquad \text{(339)}
```

ここで $`\mathbf{0}_{32}`$ は32個のゼロ・バイトである。

<span id="tnref-13"></span>[訳注13](../translation-notes.md#tn-13)

### J.4.2. キャッシュ

キャッシュ生成処理では、まずシード・ハッシュを用いて $`c_{\mathrm{size}}`$ バイトのメモリを順に埋め、次に[(Lerner 2014)](../references.md#ref-lerner2014randmemohash)が作成したRandMemoHashアルゴリズムを $`J_{\mathrm{cacherounds}}`$ 回適用する。単一バイト配列の配列である初期キャッシュ $`\mathbf{c'}`$ は、次のように構成される。

64個の単一バイトからなる配列 $`\mathbf{c}_{i}`$ を、初期キャッシュの第 $`i`$ 要素として定義する。

<span id="eq-340"></span>

```math
\mathbf{c}_{i} = \begin{cases}
\texttt{KEC512}(\mathbf{s}) & \text{if} \quad i = 0 \quad  \\
\texttt{KEC512}(\mathbf{c}_{i-1}) & \text{otherwise}
\end{cases} \qquad \text{(340)}
```

したがって $`\mathbf{c'}`$ は次のように定義できる。

<span id="eq-341"></span>

```math
\mathbf{c'}[i] = \mathbf{c}_{i} \quad \forall \quad i < n \qquad \text{(341)}
```

<span id="eq-342"></span>

```math
n = \left\lfloor\frac{c_{\mathrm{size}}}{J_{\mathrm{hashbytes}}}\right\rfloor \qquad \text{(342)}
```

キャッシュは、初期キャッシュ $`\mathbf{c'}`$ にRandMemoHashアルゴリズムを $`J_{\mathrm{cacherounds}}`$ ラウンド適用して計算する。

<span id="eq-343"></span>

```math
\mathbf{c} = E_{\mathrm{cacherounds}}(\mathbf{c'}, J_{\mathrm{cacherounds}}) \qquad \text{(343)}
```

<span id="eq-344"></span>

```math
E_{\mathrm{cacherounds}}(\mathbf{x}, y) = \begin{cases}
\mathbf{x} & \text{if} \quad y = 0 \quad  \\
E_\text{RMH}(\mathbf{x}) & \text{if} \quad y = 1 \quad  \\
E_{\mathrm{cacherounds}}(E_\text{RMH}(\mathbf{x}), y -1 ) & \text{otherwise}
\end{cases} \qquad \text{(344)}
```

1ラウンドでは、キャッシュの各部分集合を次のように変更する。

<span id="eq-345"></span>

```math
E_\text{RMH}(\mathbf{x}) = \big( E_{\mathrm{rmh}}(\mathbf{x}, 0), E_{\mathrm{rmh}}(\mathbf{x}, 1), ... , E_{\mathrm{rmh}}(\mathbf{x}, n - 1) \big){} \qquad \text{(345)}
```

<span id="eq-346"></span>

```math
\begin{gathered}
  E_{\mathrm{rmh}}(\mathbf{x}, i) = \texttt{KEC512}(\mathbf{x'}[(i - 1 + n) \bmod n] \oplus \mathbf{x'}[\mathbf{x'}[i][0] \bmod n]) \\
  \text{with} \quad \mathbf{x'} = \mathbf{x} \quad \text{except} \quad \mathbf{x'}[j] = E_{\mathrm{rmh}}(\mathbf{x}, j) \quad \forall \quad j < i
\end{gathered} \qquad \text{(346)}
```

<span id="dataset"></span>

### J.4.3. 完全データセットの計算

本質的には、疑似無作為に選択した $`J_{\mathrm{parents}}`$ 個のキャッシュ・ノードからデータを組み合わせ、それをハッシュしてデータセットを計算する。続いて、それぞれ $`J_{\mathrm{hashbytes}}`$ バイトの複数の項目によってデータセット全体を生成する。

<span id="eq-347"></span>

```math
\mathbf{d}[i] = E_{\mathrm{datasetitem}}(\mathbf{c}, i) \quad \forall \quad i < \left\lfloor\frac{d_{\mathrm{size}}}{J_{\mathrm{hashbytes}}}\right\rfloor \qquad \text{(347)}
```

単一項目の計算では、場合によってXORの非結合的な代替として、FNVハッシュ（[(Glenn Fowler 1991)](../references.md#ref-FowlerNollVo1991FNVHash)）に着想を得たアルゴリズムを用いる。

<span id="eq-348"></span>

```math
E_\text{FNV}(\mathbf{x}, \mathbf{y}) = (\mathbf{x} \cdot (\mathrm{0x01000193} \oplus \mathbf{y})) \bmod 2^{32} \qquad \text{(348)}
```

これにより、データセットの単一項目を次のように計算できる。

<span id="eq-349"></span>

```math
E_{\mathrm{datasetitem}}(\mathbf{c}, i) = E_{\mathrm{parents}}(\mathbf{c}, i, -1, \varnothing) \qquad \text{(349)}
```

<span id="eq-350"></span>

```math
E_{\mathrm{parents}}(\mathbf{c}, i, p, \mathbf{m}) = \begin{cases}
E_{\mathrm{parents}}(\mathbf{c}, i, p +1, E_{\mathrm{mix}}(\mathbf{m}, \mathbf{c}, i, p + 1)) & \text{if} \quad p < J_{\mathrm{parents}} -2 \\
E_{\mathrm{mix}}(\mathbf{m}, \mathbf{c}, i, p + 1) & \text{otherwise}
\end{cases} \qquad \text{(350)}
```

<span id="eq-351"></span>

```math
E_{\mathrm{mix}}(\mathbf{m}, \mathbf{c}, i, p) = \begin{cases}
\texttt{KEC512}(\mathbf{c}[i \bmod c_\mathrm{{size}}] \oplus i) & \text{if} \quad p = 0 \\
E_\text{FNV}\big(\mathbf{m}, \mathbf{c}[E_\text{FNV}(i \oplus p, \mathbf{m}[p \bmod \lfloor J_{\mathrm{hashbytes}} / J_{\mathrm{wordbytes}} \rfloor]) \bmod c_{\mathrm{size}}] \big) & \text{otherwise}
\end{cases} \qquad \text{(351)}
```

## J.5. プルーフ・オブ・ワーク関数

本質的には、幅 $`J_{\mathrm{mixbytes}}`$ バイトの「mix」を維持し、完全なデータセットから $`J_{\mathrm{mixbytes}}`$ バイトを繰り返し順次取得し、 $`E_\text{FNV}`$ 関数を用いてmixと結合する。 $`J_{\mathrm{mixbytes}}`$ バイトの連続アクセスを用いることで、アルゴリズムの各ラウンドが必ずRAMから完全な1ページを取得するようにし、ASICなら理論上回避できるTLB（translation lookaside buffer）ミスを最小化する。

このアルゴリズムの出力が所望の目標値を下回れば、nonceは妥当である。末尾で `KEC` を追加適用することにより、少なくとも少量の作業を行ったことの証明として提示できる中間nonceが存在する点に注意されたい。この迅速な外側のPoW検証はDDoS対策に利用できる。また、結果が偏りのない256ビット数であることを統計的に保証する役割も果たす。

PoW関数は、第1項目を圧縮mix、第2項目を圧縮mixとシード・ハッシュを連結したもののKeccak-256ハッシュとする配列を返す。

<span id="eq-352"></span>

```math
\mathtt{PoW}(H_{\not{\mathrm{n}}}, H_{\mathrm{n}}, \mathbf{d}) = \lbrace \mathbf{m}_{\mathrm{c}}(\mathtt{KEC}(\mathtt{RLP}(L_{\mathrm{H}}(H_{\not{\mathrm{n}}}))), H_{\mathrm{n}}, \mathbf{d}), \texttt{KEC}(\mathbf{s}_{\mathrm{h}}(\mathtt{KEC}(\mathtt{RLP}(L_{\mathrm{H}}(H_{\not{\mathrm{n}}}))), H_{\mathrm{n}}) + \mathbf{m}_{\mathrm{c}}(\mathtt{KEC}(\mathtt{RLP}(L_{\mathrm{H}}(H_{\not{\mathrm{n}}}))), H_{\mathrm{n}}, \mathbf{d})) \rbrace \qquad \text{(352)}
```

ここで $`H_{\not{\mathrm{n}}}`$ はnonceを除いたヘッダのハッシュである。圧縮mix $`\mathbf{m}_{\mathrm{c}}`$ は次のように得られる。

<span id="eq-353"></span>

```math
\mathbf{m}_{\mathrm{c}}(\mathbf{h}, \mathbf{n}, \mathbf{d}) = E_{\mathrm{compress}}(E_{\mathrm{accesses}}(\mathbf{d}, \sum_{i = 0}^{n_{\mathrm{mix}}} \mathbf{s}_{\mathrm{h}}(\mathbf{h}, \mathbf{n}), \mathbf{s}_{\mathrm{h}}(\mathbf{h}, \mathbf{n}), -1), -4) \qquad \text{(353)}
```

シード・ハッシュは次のとおりである。

<span id="eq-354"></span>

```math
\mathbf{s}_{\mathrm{h}}(\mathbf{h}, \mathbf{n}) = \texttt{KEC512}(\mathbf{h} + E_{\mathrm{revert}}(\mathbf{n})) \qquad \text{(354)}
```

$`E_{\mathrm{revert}}(\mathbf{n})`$ はnonce $`\mathbf{n}`$ のバイト順を反転した列を返す。

<span id="eq-355"></span>

```math
E_{\mathrm{revert}}(\mathbf{n})[i] = \mathbf{n}[\lVert \mathbf{n} \rVert -i] \qquad \text{(355)}
```

<span id="tnref-14"></span>[訳注14](../translation-notes.md#tn-14)

二つのバイト列間の「 $`+`$ 」演算子は、両方の列の連結を返すことに注意されたい。

データセット $`\mathbf{d}`$ は[付録J.4.3](#dataset)の記述どおりに得られる。

mix内で複製される列の数は次のとおりである。

<span id="eq-356"></span>

```math
n_{\mathrm{mix}} =  \left\lfloor\frac{J_{\mathrm{mixbytes}}}{J_{\mathrm{hashbytes}}}\right\rfloor \qquad \text{(356)}
```

無作為なデータセット・ノードをmixへ追加するため、 $`E_{\mathrm{accesses}}`$ 関数を用いる。

<span id="eq-357"></span>

```math
E_{\mathrm{accesses}}(\mathbf{d}, \mathbf{m}, \mathbf{s}, i) = \begin{cases}
E_{\mathrm{mixdataset}}(\mathbf{d}, \mathbf{m},  \mathbf{s}, i) & \text{if} \quad i = J_{\mathrm{accesses}} -2 \\
E_{\mathrm{accesses}}(E_{\mathrm{mixdataset}}(\mathbf{d}, \mathbf{m}, \mathbf{s}, i), \mathbf{s}, i + 1) & \text{otherwise}
\end{cases} \qquad \text{(357)}
```

<span id="tnref-15"></span>[訳注15](../translation-notes.md#tn-15)

<span id="eq-358"></span>

```math
E_{\mathrm{mixdataset}}(\mathbf{d}, \mathbf{m}, \mathbf{s}, i) = E_\text{FNV}(\mathbf{m}, E_{\mathrm{newdata}}(\mathbf{d}, \mathbf{m}, \mathbf{s}, i)) \qquad \text{(358)}
```

$`E_{\mathrm{newdata}}`$ は $`n_{\mathrm{mix}}`$ 個の要素を持つ配列を返す。

<span id="eq-359"></span>

```math
E_{\mathrm{newdata}}(\mathbf{d}, \mathbf{m}, \mathbf{s}, i)[j] = \mathbf{d}[E_\text{FNV}(i \oplus \mathbf{s}[0], \mathbf{m}[i \bmod \left\lfloor\frac{J_{\mathrm{mixbytes}}}{J_{\mathrm{wordbytes}}}\right\rfloor]) \bmod \left\lfloor\frac{d_{\mathrm{size}} / J_{\mathrm{hashbytes}}}{n_{\mathrm{mix}}}\right\rfloor \cdot n_{\mathrm{mix}} + j] \quad \forall \quad j < n_{\mathrm{mix}} \qquad \text{(359)}
```

mixは次のように圧縮する。

<span id="eq-360"></span>

```math
E_{\mathrm{compress}}(\mathbf{m}, i) = \begin{cases}
\mathbf{m} & \text{if} \quad i \geqslant \lVert \mathbf{m} \rVert - 8 \\
E_{\mathrm{compress}}(E_\text{FNV}(E_\text{FNV}(E_\text{FNV}(\mathbf{m}[i + 4], \mathbf{m}[i + 5]), \mathbf{m}[i + 6]), \mathbf{m}[i + 7]), i + 8) & \text{otherwise}
\end{cases} \qquad \text{(360)}
```
