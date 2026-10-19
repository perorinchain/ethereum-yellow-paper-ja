# Ethereum：安全な分散型汎用トランザクション台帳（Shanghai版 efc5f9a）

<div class="title-block">

**Shanghai 版 efc5f9a — 2025-02-04**

**Dr. Gavin Wood**\
Ethereum & Parity 創設者\
gavin@parity.io

</div>

<div class="abstract">

**概要。** 暗号学的に保護されたトランザクションと結び付いたブロックチェーン・パラダイムは、多数のプロジェクトを通じてその有用性を実証してきた。そのなかでも Bitcoin は最も著名なものの一つである。そうした各プロジェクトは、分散化されてはいるものの単一である計算資源上の単純なアプリケーションとみなせる。このパラダイムを、共有状態を備えたトランザクション型単一マシンと呼ぶことができる。

Ethereum は、このパラダイムを汎用化した形で実装する。さらに、それぞれが固有の状態と実行コードを持ちながら、メッセージ・パッシングの枠組みを介して相互作用できる複数の資源を提供する。本稿では、その設計、実装上の問題、そこから生まれる機会、そして将来予想される障害について論じる。

</div>

<div class="translation-notice">

**日本語訳で追加した案内。** 本書は生成AIで作成した非公式な日本語訳であり、人間による全文の校閲・検証は行っていない。誤訳、欠落、数式や解釈の誤りがある可能性があり、翻訳・訳注の正確性と完全性は保証しない。完成・校閲済みの翻訳として扱わず、原文と現行の正式仕様を確認したうえで、自身の判断と責任で利用すること。

節・付録・参考文献の順序と番号は原文に従う。原文の脚注は通常の数字1〜12で示す。翻訳時の補足・疑義は「訳注1」〜「訳注16」という別の番号で示し、[訳注一覧（日本語訳で追加）](#translator-notes)にまとめた。訳注とこの案内は原文には含まれない。

</div>

<span id="sec:introduction"></span>

# 1. はじめに

世界の大部分でインターネット接続が普及したことにより、地球規模の情報伝送は驚くほど安価になった。Bitcoin のような技術を基盤とする運動は、デフォルトの力、合意形成機構、そして社会契約の自発的な尊重を通じて、世界中で共有でき、実質的に無料で利用できる分散型価値移転システムをインターネット上に構築できることを示した。このシステムは、暗号学的に安全なトランザクションベースの状態機械を高度に特化したものだと言える。Namecoin などの後続システムは、この技術の当初の「通貨アプリケーション」を、かなり単純ではあるものの別の用途へ適応させた。

Ethereum は、この汎用技術、すなわちあらゆるトランザクションベースの状態機械という概念を構築できる基盤技術を作ろうとするプロジェクトである。さらに、これまで主流では未開拓だった計算パラダイム、すなわち信頼できるオブジェクト・メッセージング計算フレームワーク上でソフトウェアを構築するための、緊密に統合されたエンドツーエンド・システムを開発者に提供することを目指している。

<span id="ch:driving"></span>

## 1.1. 推進要因

このプロジェクトには多くの目標がある。その主要な目標の一つは、互いを信頼する手段を持たない、合意意思のある個人間のトランザクションを容易にすることである。信頼する手段がない理由には、地理的な隔たり、接続の難しさ、あるいは既存の法制度の不整合、能力不足、消極性、費用、不確実性、不便さ、腐敗などがあり得る。豊かで曖昧さのない言語によって状態変更システムを規定し、さらに合意が自律的に執行されると合理的に期待できるようシステムを設計することで、この目的を実現する手段を提供できる。

この提案システム上の取引には、現実世界ではあまり見られないいくつかの特性がある。判断が腐敗しないことは、現実にはしばしば得難いが、利害を持たないアルゴリズム的インタープリタから自然に得られる。透明性、すなわちトランザクション・ログと規則または命令コードを通じて、ある状態や判断がどのように生じたかを正確に確認できることは、人間を基盤とするシステムでは決して完全には実現しない。自然言語は必然的に曖昧であり、情報はしばしば不足し、昔ながらの偏見は容易には払拭できないからである。

総じて、利用者がどのような個人、システム、組織と相互作用する場合でも、起こり得る結果と、その結果がどのように生じ得るかについて、絶対的な確信をもって相互作用できることを保証するシステムを提供したい。

<span id="ch:previous"></span>

## 1.2. 先行研究

[(Buterin 2013)](#ref-buterin2013ethereum) は2013年11月下旬、本研究の中核を初めて提案した。その後さまざまな点で発展したが、チューリング完全な言語と、トランザクション間で事実上無制限の記憶能力とを備えたブロックチェーンという主要機能は変わっていない。

[(Dwork and Naor 1992)](#ref-dwork92pricingvia) は、計算資源を費やしたことの暗号学的証明（「プルーフ・オブ・ワーク」）を、インターネット上で価値シグナルを送る手段として利用する最初の研究を提示した。ここで価値シグナルは、何らかの通貨としてではなくスパム抑止機構として用いられたが、基本的なデータ・チャネルが*強い経済的シグナル*を運び、受信者が*信頼*に依存せず物理的な主張を行える可能性を決定的に実証した。[(Back 2002)](#ref-back2002hashcash) は後に同様の考えに基づくシステムを作った。

通貨を保護する強い経済的シグナルとしてプルーフ・オブ・ワークを利用した最初の例は、[(Vishnumurthy, Chandrakumar, and Sirer 2003)](#ref-vishnumurthy03karma:a) によるものである。この例では、ピアツーピアのファイル取引を適正に保つためにトークンが用いられ、「消費者」がサービスの対価として「供給者」にマイクロペイメントを行えるようにした。プルーフ・オブ・ワークがもたらすセキュリティ・モデルは、履歴記録を改ざんできず、悪意ある主体が支払いを偽装したりサービス提供に不当な苦情を申し立てたりできないよう、デジタル署名と台帳によって補強された。その5年後、[(Nakamoto 2008)](#ref-nakamoto2008bitcoin) は、やや広い適用範囲を持つ別のプルーフ・オブ・ワーク保護型価値トークンを導入した。このプロジェクトの成果である Bitcoin は、世界で広く採用された最初の分散型トランザクション台帳となった。

ほかのプロジェクトは Bitcoin の成功を基礎とした。いわゆるアルトコインは、プロトコルを変更することで数多くの別通貨を導入した。よく知られたものに Litecoin と Primecoin があり、[(Sprankel 2013)](#ref-sprankel2013technical) が論じている。また、プロトコルの中核となる価値内容機構を別の用途へ転用しようとしたプロジェクトもある。たとえば [(Aron 2012)](#ref-aron2012bitcoin) は、分散型名前解決システムの提供を目指す Namecoin プロジェクトを論じている。

さらに別のプロジェクトは、システムに置かれた莫大な価値と合意形成機構に投入される膨大な計算量を活用し、Bitcoin ネットワーク自体の上に構築することを目指す。[(Willett 2013)](#ref-mastercoin2013willett) が最初に提案した Mastercoin プロジェクトは、中核プロトコルに対する多数の補助部分を利用して、Bitcoin プロトコル上に多くの高水準機能を含む、より豊かなプロトコルを構築することを目指す。[(Rosenfeld et al. 2012)](#ref-colouredcoins2012rosenfeld) が提案した Coloured Coins プロジェクトは、これと似ているが、より簡素な戦略を採る。トランザクション規則を拡張して Bitcoin の基軸通貨の代替可能性を崩し、専用の「chroma-wallet」プロトコルを認識するソフトウェアによってトークンを作成し追跡できるようにする。

分散化という基盤を捨てる方向でも研究が行われてきた。[(Boutellier and Heinzen 2014)](#ref-boutellier2014pirates) が論じる Ripple は、通貨交換のための「連合型」システムを構築し、実質的に新たな金融決済システムを作ろうとした。これは、分散化という前提を捨てれば大幅な効率向上が可能であることを示した。

スマート・コントラクトに関する初期研究は [(Szabo 1997)](#ref-szabo1997formalizing) と [(Miller 1997)](#ref-miller1997future) によって行われた。1990年代頃には、合意をアルゴリズムによって執行することが、人間の協力における重要な力となり得ることが明らかになった。このようなシステムを実装する具体的な仕組みは提案されなかったものの、法の将来がそうしたシステムから大きな影響を受けるだろうと提唱された。この観点から、Ethereum はそのような*暗号法（crypto-law）*システムの汎用的実装とみなせる。

本稿で用いる用語の一覧については、[付録A](#ch:Terminology)を参照されたい。

<span id="ch:overview"></span>

# 2. ブロックチェーン・パラダイム

Ethereum は全体として、トランザクションベースの状態機械とみなせる。すなわち、ジェネシス状態から始め、トランザクションを逐次実行して、ある現在状態へと変形していく。Ethereum 世界の正準な「版」として受け入れるのは、この現在状態である。状態には、口座残高、評判、信頼関係、物理世界の情報に関するデータなどを含められる。要するに、現在コンピュータで表現できるものは何でも許容される。したがって、トランザクションは二つの状態間の妥当な弧を表す。ここで「妥当」であることが重要であり、妥当な状態変更よりも妥当でない状態変更のほうがはるかに多い。妥当でない状態変更には、たとえば、ほかの場所で同量かつ反対向きの増加を伴わずに口座残高を減少させることなどがある。妥当な状態遷移とは、トランザクションを通じて生じるものである。形式的には次のとおりである。

<span id="Upsilon_state_transition"></span>

<span id="eq-1"></span>

```math
\boldsymbol{\sigma}_{t+1} \equiv \Upsilon(\boldsymbol{\sigma}_{t}, T) \qquad \text{(1)}
```

ここで $`\Upsilon`$ は Ethereum の状態遷移関数である。Ethereum における $`\Upsilon`$ と $`\boldsymbol{\sigma}`$ は、既存の同種システムよりも大幅に強力である。 $`\Upsilon`$ によって構成要素は任意の計算を実行でき、 $`\boldsymbol{\sigma}`$ によって構成要素はトランザクション間で任意の状態を保存できる。

トランザクションはブロックにまとめられ、ブロックは参照手段として暗号学的ハッシュを用いて連結される。ブロックは履歴台帳として機能し、一連のトランザクションを、直前のブロックおよび最終状態の識別子とともに記録する（ただし最終状態自体は格納しない。それでは大きくなりすぎるためである）。

形式的には、次のように拡張される。

<span id="eq-2"></span><span id="eq-3"></span><span id="eq-4"></span>

```math
\begin{aligned}
\boldsymbol{\sigma}_{t+1} & \equiv & \Pi(\boldsymbol{\sigma}_{t}, B) & \qquad \text{(2)} \\
B & \equiv & (..., (T_0, T_1, ...), ...) & \qquad \text{(3)} \\
\Pi(\boldsymbol{\sigma}, B) & \equiv & \Upsilon(\Upsilon(\boldsymbol{\sigma}, T_0), T_1) ... & \qquad \text{(4)}
\end{aligned}
```

ここで [$`B`$](#block) は当該ブロックであり、いくつかのほかの構成要素とともに一連のトランザクションを含む。また、 $`\Pi`$ はトランザクションに対するブロック水準の状態遷移関数である[^1]。

これがブロックチェーン・パラダイムの基礎である。このモデルは Ethereum のみならず、これまでのあらゆる分散型合意ベースのトランザクション・システムを支える骨格をなす。

## 2.1. 価値

ネットワーク内での計算にインセンティブを与えるため、価値を伝達する合意済みの方法が必要である。この問題に対処するため、Ethereum は Ether という固有通貨を持つ。Ether は ETH としても知られ、古英語の Ð と表記されることもある。Ether の最小補助単位、したがって通貨のすべての整数値を数える単位は Wei である。1 Ether は $`10^{18}`$ Wei と定義される。Ether にはほかにも次の補助単位がある。

<div class="center">

| 倍率 | 名称   |
|-----------:|:-------|
|     $`10^0`$ | Wei    |
|     $`10^9`$ | Gwei   |
|  $`10^{12}`$ | Szabo  |
|  $`10^{15}`$ | Finney |
|  $`10^{18}`$ | Ether  |

</div>

本稿を通じて、Ether、通貨、残高または支払いの文脈で価値に言及する場合は、Wei 単位で数えるものとする。

## 2.2. どの履歴か

システムは分散化されており、すべての当事者に、既存の古いブロックを基礎として新しいブロックを作成する機会があるため、結果として生じる構造は必然的にブロックの木となる。この木構造を通る根（[ジェネシス・ブロック](#Genesis_Block)）から葉（最新のトランザクションを含むブロック）までの経路、すなわちブロックチェーンのうち、どれを採るかについて合意を形成するには、合意された方式がなければならない。ブロック木を根から葉へ下るどの経路が「最善」のブロックチェーンであるかについてノード間に不一致が生じれば、*フォーク*が発生する。

これは、ある時点（ブロック）以降、システムの複数の状態が共存し得ることを意味する。あるノード群は一つのブロックが正準なトランザクションを含むと信じ、別のノード群は別のブロックが正準であると信じる。そのブロックには根本的に異なる、または互換性のないトランザクションが含まれる可能性がある。そこから生じる不確実性はシステム全体に対する信頼を失わせる可能性が高いため、これは何としても避けなければならない。

*Paris* ハードフォーク以降、新しいブロックに関する合意形成は *Beacon Chain* と呼ばれるプロトコルが管理する。これは Ethereum の*合意レイヤー*として知られ、Ethereum ブロックの正準な履歴を決定する規則を定める。本書が記述するのは Ethereum の*実行レイヤー*である。実行レイヤーは、Ethereum 仮想マシンの状態と相互作用し、それを更新する規則を定める。合意レイヤーは[合意仕様](https://github.com/ethereum/consensus-specs)により詳しく記述されている。Ethereum の正準状態を決定するために合意レイヤーをどのように利用するかは、[第11節](#ch:blocktree_to_blockchain)で論じる。

プロトコルには多数の更新が行われてきたため、Ethereum には多くの版がある。これらの更新が発生する条件は、次のように規定できる。

- *Paris* より前の更新では、特定のブロック番号

- *Paris* 更新では、*終端総難易度（terminal total difficulty）*への到達

- *Paris* より後の更新では、特定のブロック・タイムスタンプ

本書は *Shanghai* 版を記述する。

ある経路の履歴を遡るには、本書の複数の版を参照しなければならない。Ethereum メインネットワークにおけるプロトコル更新のブロック番号は次のとおりである[^2]。

<div class="center">

| 名称                             | 最初のブロック番号 |
|:---------------------------------|-------------------:|
| $`F_{\mathrm{Homestead}}`$         |            1150000 |
| $`F_{\mathrm{Tangerine Whistle}}`$ |            2463000 |
| $`F_{\mathrm{Spurious Dragon}}`$   |            2675000 |
| $`F_{\mathrm{Byzantium}}`$         |            4370000 |
| $`F_{\mathrm{Constantinople}}`$    |            7280000 |
| $`F_{\mathrm{Petersburg}}`$        |            7280000 |
| $`F_{\mathrm{Istanbul}}`$          |            9069000 |
| $`F_{\mathrm{Muir Glacier}}`$      |            9200000 |
| $`F_{\mathrm{Berlin}}`$            |           12244000 |
| $`F_{\mathrm{London}}`$            |           12965000 |
| $`F_{\mathrm{Arrow Glacier}}`$     |           13773000 |
| $`F_{\mathrm{Gray Glacier}}`$      |           15050000 |
| $`F_{\mathrm{Paris}}`$             |           15537394 |
| $`F_{\mathrm{Shanghai}}`$          |           17034870 |

</div>

時として、プロトコル変更について主体間の合意が得られず、永続的なフォークが発生する。分岐したブロックチェーンを区別するため、[(Buterin 2016)](#ref-EIP-155) の EIP-155 はチェーンIDという概念を導入した。本書ではこれを $`\beta`$ と表す。Ethereum メインネットワークでは次のとおりである。

<span id="chain_id"></span>

<span id="eq-5"></span>

```math
\beta = 1 \qquad \text{(5)}
```

<span id="ch:conventions"></span>

# 3. 表記規約

形式的記法にはいくつかの組版上の規約を用いる。その一部は本稿にかなり固有のものである。

高度に構造化された「最上位」の状態値の二つの集合は、太字のギリシャ小文字で表す。これらは、 $`\boldsymbol{\sigma}`$ （またはその変種）で表すワールド状態と、 $`\boldsymbol{\mu}`$ で表すマシン状態に分類される。

高度に構造化された値を操作する関数は、Ethereum 状態遷移関数 [$`\Upsilon`$](#Upsilon_state_transition) のように、ギリシャ大文字で表す。

大部分の関数には大文字のラテン文字を用いる。たとえば $`C`$ は一般コスト関数である。特殊化した変種を表すため添字を付けることがあり、たとえば [$`C_\text{SSTORE}`$](#C__SSTORE) は [SSTORE](#SSTORE) 演算のコスト関数である。特殊化された関数や外部で定義される可能性のある関数は、タイプライタ体で表すことがある。たとえば Keccak-256 ハッシュ関数（最終版 SHA-3 仕様ではなく、[(Bertoni et al. 2011)](#ref-Keccak) による SHA-3 コンテスト優勝案の第3版に基づく）は $`\texttt{KEC}`$ と表し、通常は単に Keccak と呼ぶ。また $`\texttt{KEC512}`$ は Keccak-512 ハッシュ関数を指す。

タプルは通常、大文字で表す。たとえば $`T`$ は Ethereum のトランザクションを表す。この記号は、そのように定義されていれば、個々の構成要素を参照する添字を付けられる。たとえば [$`T_{\mathrm{n}}`$](#transaction_nonce) は当該トランザクションの nonce を表す。添字の字体はその型を示すために用いる。たとえば大文字の添字は、添字で構成要素を参照できるタプルを示す。

スカラーと固定長バイト列（同義語として配列）は、通常の小文字で表す。たとえば本書では $`n`$ を[トランザクション nonce](#transaction_nonce) の表記に用いる。特に固有の意味を持つものにはギリシャ文字を用いることがあり、たとえば $`\delta`$ は所与の演算がスタック上に必要とする項目数である。

任意長の列は通常、太字の小文字で表す。たとえば $`\mathbf{o}`$ はメッセージ呼び出しの出力データとして与えられるバイト列を表す。特に重要な値には太字の大文字を用いることがある。

本書を通じて、スカラーは非負整数であり、したがって集合 $`\mathbb{N}`$ に属すると仮定する。すべてのバイト列からなる集合を $`\mathbb{B}`$ とし、[付録B](#app:rlp)で形式的に定義する。列の集合を特定の長さのものに制限する場合は添字で表す。したがって、長さ32のすべてのバイト列からなる集合を $`\mathbb{B}_{32}`$ 、 $`2^{256}`$ 未満のすべての非負整数からなる集合を $`\mathbb{N}_{256}`$ と呼ぶ。これは[第4.4節](#subsec:The_Block)で形式的に定義する。

角括弧は、列の個々の構成要素または部分列に索引付けして参照するために用いる。たとえば $`\boldsymbol{\mu}_{\mathbf{s}}[0]`$ はマシンのスタック上の最初の項目を表す。部分列では、省略記号を使って両端の要素を含む範囲を指定する。たとえば $`\boldsymbol{\mu}_{\mathbf{m}}[0..31]`$ はマシン・メモリの最初の32項目を表す。

それ自体がタプルであるアカウントの列からなる大域状態 $`\boldsymbol{\sigma}`$ の場合、角括弧は個々のアカウントを参照するために用いる。

既存値の変種を考えるときは、所与の定義スコープ内で、変更前の「入力」値をプレースホルダ $`\Box`$ で表すと仮定すれば、変更後の利用可能な値を $`\Box'`$ 、中間値を $`\Box^{*}`$ 、 $`\Box^{**}`$ などと表す、という規則に従う。ごく特殊な場合には、可読性を最大にするため、かつ意味に曖昧さがない場合に限って、特に注目すべき中間値を英数字の添字で表すことがある。

既存関数の利用を考えるとき、関数 $`f`$ に対する関数 [$`f^{*}`$](#general_element_wise_sequence_transformation_f_pow_asterisk) は、列同士を写像する、同様の要素単位版の関数を表す。これは[第4.4節](#subsec:The_Block)で形式的に定義する。

本書を通じて、有用な関数をいくつか定義する。よく用いるものの一つが $`\ell`$ であり、所与の列の最後の項目を値とする。

<span id="eq-6"></span>

```math
\ell(\mathbf{x}) \equiv \mathbf{x}[\lVert \mathbf{x} \rVert - 1] \qquad \text{(6)}
```

<span id="ch:bst"></span>

# 4. ブロック、状態、トランザクション

Ethereum の基礎概念を導入したので、トランザクション、ブロック、状態の意味をさらに詳しく論じる。

<span id="ch:state"></span>

## 4.1. ワールド状態

ワールド状態（*状態*）は、アドレス（160ビット識別子）からアカウント状態（RLP として直列化されるデータ構造、[付録B](#app:rlp)参照）への写像である。ワールド状態自体はブロックチェーンに格納されないが、実装はこの写像を修正 Merkle Patricia 木（*トライ*、[付録D](#app:trie)参照）で維持するものと仮定する。トライには、バイト配列からバイト配列への写像を維持する単純なデータベース・バックエンドが必要であり、この基盤データベースを状態データベースと呼ぶ。これにはいくつかの利点がある。第一に、この構造のルート・ノードは暗号学的にすべての内部データに依存するため、そのハッシュをシステム状態全体の安全な識別子として利用できる。第二に、不変データ構造であるため、ルート・ハッシュが既知の過去状態は、ルート・ハッシュを対応する値へ変更するだけで呼び戻せる。こうしたルート・ハッシュはすべてブロックチェーンに格納されるため、古い状態へ容易に戻せる。

アカウント状態 $`\boldsymbol{\sigma}[a]`$ は、次の4フィールドからなる。

<span id="account_nonce"></span>

nonce
: このアドレスから送信されたトランザクション数に等しいスカラー値。コードが関連付けられたアカウントの場合は、このアカウントが行ったコントラクト作成数に等しい。状態 $`\boldsymbol{\sigma}`$ におけるアドレス $`a`$ のアカウントについて、形式的には $`\boldsymbol{\sigma}[a]_{\mathrm{n}}`$ と表す。

balance
: このアドレスが所有する Wei の数量に等しいスカラー値。形式的には $`\boldsymbol{\sigma}[a]_{\mathrm{b}}`$ と表す。

storageRoot
: アカウントのストレージ内容（256ビット整数値間の写像）を符号化する Merkle Patricia 木のルート・ノードの256ビット・ハッシュ。これは、256ビット整数キーの Keccak 256ビット・ハッシュから、RLP 符号化された256ビット整数値への写像としてトライに符号化される。このハッシュを形式的には $`\boldsymbol{\sigma}[a]_{\mathrm{s}}`$ と表す。

codeHash
: このアカウントの EVM コードのハッシュ。このアドレスがメッセージ呼び出しを受けると、このコードが実行される。このようなコード断片はすべて、後で取得できるよう対応するハッシュの下で状態データベースに格納される。このハッシュを形式的には $`\boldsymbol{\sigma}[a]_{\mathrm{c}}`$ と表す。したがって、 $`\texttt{KEC}(\mathbf{b}) = \boldsymbol{\sigma}[a]_{\mathrm{c}}`$ となるコードを $`\mathbf{b}`$ と表せる。

通常参照したいのはトライのルート・ハッシュではなく、内部に格納されたキー／値ペアの集合であるため、次の便利な同値関係を定義する。

<span id="eq-7"></span>

```math
\texttt{TRIE}\big(L_{\mathrm{I}}^{*}(\boldsymbol{\sigma}[a]_{\mathbf{s}})\big) \equiv \boldsymbol{\sigma}[a]_{\mathrm{s}} \qquad \text{(7)}
```

トライ内のキー／値ペア集合に対する縮約関数 $`L_{\mathrm{I}}^{*}`$ は、次に示す基礎関数 $`L_{\mathrm{I}}`$ を要素ごとに適用する変換として定義される。

<span id="eq-8"></span>

```math
L_{\mathrm{I}}\big( (k, v) \big) \equiv \big(\texttt{KEC}(k), \texttt{RLP}(v)\big) \qquad \text{(8)}
```

ここで、

<span id="eq-9"></span>

```math
k \in \mathbb{B}_{32} \quad \wedge \quad v \in \mathbb{N} \qquad \text{(9)}
```

$`\boldsymbol{\sigma}[a]_{\mathbf{s}}`$ はアカウントの「物理的」な構成要素ではなく、後の直列化には寄与しないものと理解されたい。

**codeHash** フィールドが空文字列の Keccak-256 ハッシュ、すなわち $`\boldsymbol{\sigma}[a]_{\mathrm{c}} = \texttt{KEC}\big(()\big)`$ であれば、そのノードは単純アカウントを表し、「非コントラクト」アカウントと呼ばれることもある。

したがって、ワールド状態の縮約関数 $`L_{\mathrm{S}}`$ を次のように定義できる。

<span id="eq-10"></span>

```math
L_{\mathrm{S}}(\boldsymbol{\sigma}) \equiv \{ p(a): \boldsymbol{\sigma}[a] \neq \varnothing \} \qquad \text{(10)}
```

ここで、

<span id="eq-11"></span>

```math
p(a) \equiv  \big(\texttt{KEC}(a), \texttt{RLP}\big( (\boldsymbol{\sigma}[a]_{\mathrm{n}}, \boldsymbol{\sigma}[a]_{\mathrm{b}}, \boldsymbol{\sigma}[a]_{\mathrm{s}}, \boldsymbol{\sigma}[a]_{\mathrm{c}}) \big) \big) \qquad \text{(11)}
```

である。

この関数 $`L_{\mathrm{S}}`$ はトライ関数とともに用いられ、ワールド状態の短い識別子（ハッシュ）を与える。次を仮定する。

<span id="eq-12"></span>

```math
\forall a: \boldsymbol{\sigma}[a] = \varnothing \; \vee \; (a \in \mathbb{B}_{20} \; \wedge \; v(\boldsymbol{\sigma}[a])) \qquad \text{(12)}
```

ここで $`v`$ はアカウント妥当性関数である。

<span id="eq-13"></span>

```math
\quad v(x) \equiv x_{\mathrm{n}} \in \mathbb{N}_{256} \wedge x_{\mathrm{b}} \in \mathbb{N}_{256} \wedge x_{\mathrm{s}} \in \mathbb{B}_{32} \wedge x_{\mathrm{c}} \in \mathbb{B}_{32} \qquad \text{(13)}
```

コードを持たず、nonceと残高がともにゼロであるとき、アカウントは*空（empty）*である。

<span id="eq-14"></span>

```math
\mathtt{EMPTY}(\boldsymbol{\sigma}, a) \quad\equiv\quad \boldsymbol{\sigma}[a]_{\mathrm{c}} = \texttt{KEC}\big(()\big) \wedge \boldsymbol{\sigma}[a]_{\mathrm{n}} = 0 \wedge \boldsymbol{\sigma}[a]_{\mathrm{b}} = 0 \qquad \text{(14)}
```

呼び出し可能なプリコンパイル済みコントラクトであっても、アカウント状態が空であり得る。これは通常、その振る舞いを記述するコードがアカウント状態に含まれないためである。

アカウント状態が存在しないか空であるとき、そのアカウントは*死んでいる（dead）*という。

<span id="eq-15"></span>

```math
\mathtt{DEAD}(\boldsymbol{\sigma}, a) \quad\equiv\quad \boldsymbol{\sigma}[a] = \varnothing \vee \mathtt{EMPTY}(\boldsymbol{\sigma}, a) \qquad \text{(15)}
```

<span id="subsec:transaction"></span>

## 4.2. トランザクション

トランザクション（形式的には $`T`$ ）は、Ethereum の範囲外にいる主体が作成する、暗号学的に署名された一つの命令である。トランザクションの送信者をコントラクトとすることはできない。最終的な外部主体は人間であると仮定するが、トランザクションの作成と配布にはソフトウェア・ツールが用いられる[^3]。[(Zoltu 2020)](#ref-EIP-2718) の EIP-2718 は異なるトランザクション型という概念を導入した。プロトコルの *London* 版時点で、トランザクション型は0（レガシー）、1（[(Buterin and Swende 2020b)](#ref-EIP-2930) の EIP-2930）、2（[(Buterin et al. 2019)](#ref-EIP-1559) の EIP-1559）の3種類である。さらに、トランザクションには、メッセージ呼び出しをもたらすものと、コードが関連付けられた新しいアカウントを作成するもの（非形式的には「コントラクト作成」と呼ばれる）の二つの下位型がある。すべてのトランザクション型は、次の共通フィールドを指定する。

<span id="tx_type"></span>

type
: EIP-2718 トランザクション型。形式的には $`T_{\mathrm{x}}`$ 。

nonce
: 送信者が送信したトランザクション数に等しいスカラー値。形式的には $`T_{\mathrm{n}}`$ 。

gasLimit
: このトランザクションの実行に使用できる gas の最大量に等しいスカラー値。これは計算を行う前に前払いされ、後から増やすことはできない。形式的には $`T_{\mathrm{g}}`$ 。

to
: メッセージ呼び出しの受信者の160ビット・アドレス。コントラクト作成トランザクションの場合は、ここでは $`\mathbb{B}_0`$ の唯一の要素を表す $`\varnothing`$ 。形式的には $`T_{\mathrm{t}}`$ 。

value
: メッセージ呼び出しの受信者へ移転する Wei の数量、またはコントラクト作成の場合は新たに作成されるアカウントへ付与する Wei の数量に等しいスカラー値。形式的には $`T_{\mathrm{v}}`$ 。

<span id="T__r_T__s"></span>

r, s
: トランザクションの署名に対応し、その送信者を決定するために用いる値。形式的には $`T_{\mathrm{r}}`$ と $`T_{\mathrm{s}}`$ 。[付録F](#app:signing)で詳述する。

EIP-2930（型1）および EIP-1559（型2）トランザクションは、さらに次のフィールドを持つ。

accessList
: ウォームアップするアクセス項目のリスト。形式的には $`T_{\mathbf{A}}`$ 。各アクセス・リスト項目 $`E`$ は、アカウント・アドレスとストレージ・キーのリストとのタプルである： $`E \equiv (E_{\mathrm{a}}, E_{\mathbf{s}})`$ 。

chainId
: チェーンID。形式的には $`T_{\mathrm{c}}`$ 。ネットワークのチェーンID [$`\beta`$](#chain_id) と等しくなければならない。

yParity
: 署名の Y パリティ。形式的には $`T_{\mathrm{y}}`$ 。

レガシー・トランザクションは **accessList** を持たず（ $`T_{\mathbf{A}}=()`$ ）、レガシー・トランザクションの **chainId** と **yParity** は一つの値に結合される。

w
: Y パリティと、場合によってはチェーンIDを符号化するスカラー値。形式的には $`T_{\mathrm{w}}`$ 。 $`T_{\mathrm{w}} = 27 + T_{\mathrm{y}}`$ または $`T_{\mathrm{w}} = 2\beta + 35 + T_{\mathrm{y}}`$ （[(Buterin 2016)](#ref-EIP-155) の EIP-155 参照）。

許容する gas 価格の指定方法は、型2と、型0および型1のトランザクションとで異なる。型2トランザクションは、支払う*優先手数料*[^4]を明示的に制限することで、EIP-1559 が導入した gas 市場の改善をより活用する。型2トランザクションは gas に関する次の二つのフィールドを持つ。

maxFeePerGas
: このトランザクションの実行によって生じるすべての計算コストについて、*gas* 1単位当たりに支払う Wei の最大量に等しいスカラー値。形式的には $`T_{\mathrm{m}}`$ 。

maxPriorityFeePerGas
: トランザクションを収録するインセンティブとして、ブロックの手数料受取人に支払う Wei の最大量に等しいスカラー値。形式的には $`T_{\mathrm{f}}`$ 。

これに対し、型0および型1トランザクションは gas 価格を単一の値として指定する。

gasPrice
: このトランザクションの実行によって生じるすべての計算コストについて、*gas* 1単位当たりに支払う Wei の数量に等しいスカラー値。形式的には $`T_{\mathrm{p}}`$ [^5]。

さらに、コントラクト作成トランザクションは（トランザクション型にかかわらず）次を含む。

init
: アカウント初期化手続きの EVM コードを指定する、サイズ無制限のバイト配列。形式的には $`T_{\mathbf{i}}`$ 。

<span id="tnref-1"></span>[訳注1](#tn-1)

**init** は EVM コード断片であり、**body** を返す。**body** は、そのアカウントがメッセージ呼び出しを受けるたびに（トランザクションを介する場合も、コードの内部実行による場合も）実行される第2のコード断片である。**init** はアカウント作成時に一度だけ実行され、その直後に破棄される。

これに対し、メッセージ呼び出しトランザクションは次を含む。

data
: メッセージ呼び出しの入力データを指定する、サイズ無制限のバイト配列。形式的には $`T_{\mathbf{d}}`$ 。

[付録F](#app:signing)では、トランザクションを送信者へ写像する関数 $`S`$ を規定する。この写像は SECP-256k1 曲線の ECDSA により、後ろの三つの署名フィールドを除いたトランザクションのハッシュを署名対象データとして用いて行われる。ここでは、所与のトランザクション $`T`$ の送信者を $`S(T)`$ で表せるとだけ仮定する。

<span id="eq-16"></span>

```math
L_{\mathrm{T}}(T) \equiv \begin{cases}
(T_{\mathrm{n}}, T_{\mathrm{p}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, T_{\mathrm{w}}, T_{\mathrm{r}}, T_{\mathrm{s}}) & \text{if} \; T_{\mathrm{x}} = 0 \\
(T_{\mathrm{c}}, T_{\mathrm{n}}, T_{\mathrm{p}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, T_{\mathbf{A}}, T_{\mathrm{y}}, T_{\mathrm{r}}, T_{\mathrm{s}}) & \text{if} \; T_{\mathrm{x}} = 1 \\
(T_{\mathrm{c}}, T_{\mathrm{n}}, T_{\mathrm{f}}, T_{\mathrm{m}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, T_{\mathbf{A}}, T_{\mathrm{y}}, T_{\mathrm{r}}, T_{\mathrm{s}}) & \text{if} \; T_{\mathrm{x}} = 2 \\
\end{cases} \qquad \text{(16)}
```

ここで、

<span id="eq-17"></span>

```math
\mathbf{p} \equiv \begin{cases}
T_{\mathbf{i}} & \text{if}\ T_{\mathrm{t}} = \varnothing \\
T_{\mathbf{d}} & \text{otherwise}
\end{cases} \qquad \text{(17)}
```

ここで、アクセス・リスト $`T_{\mathbf{A}}`$ と任意長のバイト配列 $`T_{\mathbf{i}}`$ および $`T_{\mathbf{d}}`$ を除き、すべての構成要素はRLPによって整数値として解釈されるものとする。

<span id="eq-18"></span>

```math
\begin{array}{lclclc}
T_{\mathrm{x}} \in \{0, 1, 2\} & \wedge & T_{\mathrm{c}} = \beta & \wedge & T_{\mathrm{n}} \in \mathbb{N}_{256} & \wedge \\
T_{\mathrm{p}} \in \mathbb{N}_{256} & \wedge & T_{\mathrm{g}} \in \mathbb{N}_{256} & \wedge & T_{\mathrm{v}} \in \mathbb{N}_{256} & \wedge \\
T_{\mathrm{w}} \in \mathbb{N}_{256} & \wedge & T_{\mathrm{r}} \in \mathbb{N}_{256} & \wedge & T_{\mathrm{s}} \in \mathbb{N}_{256} & \wedge \\
T_{\mathrm{y}} \in \mathbb{N}_{1} & \wedge & T_{\mathbf{d}} \in \mathbb{B} & \wedge & T_{\mathbf{i}} \in \mathbb{B} & \wedge \\
T_{\mathrm{m}} \in \mathbb{N}_{256} & \wedge & T_{\mathrm{f}} \in \mathbb{N}_{256}
\end{array} \qquad \text{(18)}
```

ここで、

<span id="eq-19"></span>

```math
\mathbb{N}_{\mathrm{n}} = \{ P: P \in \mathbb{N} \wedge P < 2^n \} \qquad \text{(19)}
```

アドレス・ハッシュ $`T_{\mathbf{t}}`$ はやや異なる。これは20バイトのアドレス・ハッシュであるか、コントラクト作成トランザクションの場合（したがって形式的には $`\varnothing`$ に等しい）はRLPの空バイト列、すなわち $`\mathbb{B}_0`$ の要素となる。

<span id="eq-20"></span>

```math
T_{\mathbf{t}} \in \begin{cases} \mathbb{B}_{20} & \text{if} \quad T_{\mathrm{t}} \neq \varnothing \\
\mathbb{B}_{0} & \text{otherwise}\end{cases} \qquad \text{(20)}
```

<span id="subsec:The_Withdrawal"></span>

## 4.3. 引き出し

引き出し（形式的には *W*）は、合意レイヤーのバリデータがステーク済みEtherの一部を引き出すことを記述するデータのタプルである。引き出しはブロックチェーンの合意レイヤーで作成・検証された後、実行レイヤーへ送られる。引き出しは次のフィールドから構成される。

globalIndex
: ゼロから始まり単調に増加する引き出しインデックスであり、この引き出しの一意な識別子として機能する。形式的には $`W_{\mathrm{g}}`$ 。

validatorIndex
: この引き出しに対応する合意レイヤーのバリデータのインデックス。形式的には $`W_{\mathrm{v}}`$ 。

recipient
: この引き出しによるEtherを受け取る20バイトのアドレス。形式的には $`W_{\mathrm{r}}`$ 。

amount
: Gwei（ $`10^9`$ Wei）単位で表したゼロではないEther量。形式的には $`W_{\mathrm{a}}`$ 。

引き出しの直列化を次のように定義する。

<span id="eq-21"></span>

```math
L_{\mathrm{W}}(W) \equiv
(W_{\mathrm{g}}, W_{\mathrm{v}}, W_{\mathrm{r}}, T_{\mathrm{a}}) \qquad \text{(21)}
```

<span id="tnref-2"></span>[訳注2](#tn-2)

ここで、20バイトのアドレスである $`W_\mathbf{r}`$ を除き、すべての構成要素はRLPによって整数値として解釈されるものとする。

<span id="eq-22"></span>

```math
\begin{array}{lclc}
W_{\mathrm{g}} \in \mathbb{N}_{64} & \wedge & W_{\mathrm{v}} \in \mathbb{N}_{64} & \wedge \\
W_{\mathrm{r}} \in \mathbb{B}_{20} & \wedge & W_{\mathrm{a}} \in \mathbb{N}_{64}
\end{array} \qquad \text{(22)}
```

<span id="subsec:The_Block"></span>

<span id="block"></span>

## 4.4. ブロック

Ethereumのブロックは、関連情報の集合（ブロック*ヘッダ*と呼ばれる） $`H`$ と、そこに含まれるトランザクションに対応する情報 $`\mathbf{T}`$ 、<span id="ommerheaders"></span>現在は非推奨となった属性 $`\mathbf{U}`$ 、および *Shanghai* ハードフォーク以降は合意レイヤーから送られるバリデータ引き出しの集合 $`\mathbf{W}`$ からなる。 $`\mathbf{U}`$ には *Paris* ハードフォーク以前、親が現在のブロックの親の親と等しいブロック（このようなブロックは*ommer*[^6]と呼ばれた）のヘッダが含まれていた。ブロック・ヘッダは次の情報を含む。

parentHash
: 親ブロックのヘッダ全体のKeccak 256ビット・ハッシュ。形式的には $`H_{\mathrm{p}}`$ 。

ommersHash
: プルーフ・オブ・ワーク合意の置換により現在は非推奨となった256ビットのハッシュ・フィールド。現在は定数 $`\texttt{KEC}(\texttt{RLP}(()))`$ である。形式的には $`H_{\mathrm{o}}`$ 。

beneficiary
: このブロックの優先手数料が送金される160ビットのアドレス。形式的には $`H_{\mathrm{c}}`$ 。

stateRoot
: すべてのトランザクションと引き出しを実行し、最終化を適用した後の状態トライのルート・ノードのKeccak 256ビット・ハッシュ。形式的には $`H_{\mathrm{r}}`$ 。

transactionsRoot
: ブロックのトランザクション・リスト部分にある各トランザクションを格納したトライ構造のルート・ノードのKeccak 256ビット・ハッシュ。形式的には $`H_{\mathrm{t}}`$ 。

receiptsRoot
: ブロックのトランザクション・リスト部分にある各トランザクションのレシートを格納したトライ構造のルート・ノードのKeccak 256ビット・ハッシュ。形式的には $`H_{\mathrm{e}}`$ 。

logsBloom
: トランザクション・リスト内の各トランザクションのレシートにある各ログ項目に含まれる、索引付け可能な情報（ロガーのアドレスとログ・トピック）から構成されるBloomフィルタ。形式的には $`H_{\mathrm{b}}`$ 。

difficulty
: プルーフ・オブ・ワーク合意の置換により現在は非推奨となったスカラー・フィールド。0に設定される。形式的には $`H_{\mathrm{d}}`$ 。

number
: 祖先ブロック数に等しいスカラー値。ジェネシス・ブロックの値は0である。形式的には [$`H_{\mathrm{i}}`$](#block_number_H__i)。

gasLimit
: ブロック当たりの現在のgas消費上限に等しいスカラー値。形式的には $`H_{\mathrm{l}}`$ 。

<span id="H__g"></span>

gasUsed
: このブロックのトランザクションで使用されたgasの総量に等しいスカラー値。形式的には $`H_{\mathrm{g}}`$ 。

timestamp
: このブロックの生成時点におけるUnixの `time()` の妥当な出力に等しいスカラー値。形式的には [$`H_{\mathrm{s}}`$](#block_timestamp_H__s)。

extraData
: このブロックに関連するデータを含む任意のバイト配列。32バイト以下でなければならない。形式的には $`H_{\mathrm{x}}`$ 。

prevRandao
: 直前のブロックを処理した後のビーコン状態における最新のRANDAO mix[^7]。形式的には $`H_{\mathrm{a}}`$ 。

<span id="H__n"></span>

nonce
: プルーフ・オブ・ワーク合意の置換により現在は非推奨となった64ビット値。`0x0000000000000000` に設定される。形式的には [$`H_{\mathrm{n}}`$](#H__n)。

<span id="block_baseFeePerGas_H__f"></span>

baseFeePerGas
: 消費されるgas 1単位ごとにバーンされるwei量に等しいスカラー値。形式的には [$`H_{\mathrm{f}}`$](#H__f)。

<span id="H__w"></span>

withdrawalsRoot
: このブロックについて合意レイヤーから送られた各引き出し操作を格納したトライ構造のルート・ノードのKeccak 256ビット・ハッシュ。形式的には [$`H_{\mathrm{w}}`$](#H__w)。

ブロックの残る三つの構成要素は、トランザクション列 $`B_{\mathbf{T}}`$ 、以前ommerブロック・ヘッダ用に予約されていた空配列 $`B_{\mathbf{U}}`$ 、および引き出し列 $`B_{\mathbf{W}}`$ である。形式的にはブロック $`B`$ を次のように表す。

<span id="eq-23"></span>

```math
B \equiv (B_{\mathrm{H}}, B_{\mathbf{T}}, B_{\mathbf{U}}, B_{\mathbf{W}}) \qquad \text{(23)}
```

<span id="Transaction_Receipt"></span>

### 4.4.1. トランザクション・レシート

ゼロ知識証明の構成、索引付け、検索に有用となり得るトランザクション情報を符号化するため、実行によって得られる一定の情報を含むレシートを各トランザクションについて符号化する。第 $`i`$ トランザクションのレシートを $`B_{\mathbf{R}}[i]`$ と表し、インデックスをキーとする[トライ](#trie)に格納する。そのルートはヘッダに [$`H_{\mathrm{e}}`$](#Receipts_Root_H__e) として記録される。

トランザクション・レシート $`R`$ は五つの要素からなるタプルである。すなわち、トランザクションの型 $`R_{\mathrm{x}}`$ 、ステータス・コード $`R_{\mathrm{z}}`$ 、そのトランザクションが生じた直後の時点で当該レシートを含むブロック内において使用済みの累積gas $`R_{\mathrm{u}}`$ 、トランザクションの実行によって生成されたログ集合 [$`R_\mathbf{l}`$](#RLP_serialisation_of_a_sequence_of_other_items_R__l_math_def)、およびそれらのログ情報から構成されるBloomフィルタ [$`R_{\mathrm{b}}`$](#RLP_serialisation_of_a_byte_array_R__b_math_def) である。

<span id="eq-24"></span>

```math
R \equiv (R_{\mathrm{x}}, R_{\mathrm{z}}, R_{\mathrm{u}}, R_{\mathrm{b}}, R_{\mathbf{l}}) \qquad \text{(24)}
```

$`R_{\mathrm{x}}`$ は対応するトランザクションの[型](#tx_type)に等しい。

関数 $`L_{\mathrm{R}}`$ は、トランザクション・レシートをRLP直列化されたバイト配列へ変換するために準備する。

<span id="eq-25"></span>

```math
L_{\mathrm{R}}(R) \equiv (R_{\mathrm{z}}, R_{\mathrm{u}}, R_{\mathrm{b}}, R_{\mathbf{l}}) \qquad \text{(25)}
```

ステータス・コード $`R_{\mathrm{z}}`$ は非負整数である。

<span id="eq-26"></span>

```math
R_{\mathrm{z}} \in \mathbb{N} \qquad \text{(26)}
```

累積使用gas $`R_{\mathrm{u}}`$ は非負整数であり、ログBloom $`R_{\mathrm{b}}`$ は2048ビット（256バイト）のハッシュである。

<span id="eq-27"></span>

```math
R_{\mathrm{u}} \in \mathbb{N} \quad \wedge \quad R_{\mathrm{b}} \in \mathbb{B}_{256} \qquad \text{(27)}
```

列 $`R_{\mathbf{l}}`$ はログ項目の列 $`(O_0, O_1, ...)`$ である。ログ項目 $`O`$ は、ロガーのアドレス $`O_a`$ 、空でもよい32バイトのログ・トピック列 $`O_{\mathbf{t}}`$ 、および任意バイト数のデータ $`O_{\mathbf{d}}`$ からなるタプルである。

<span id="eq-28"></span>

```math
O \equiv (O_{\mathrm{a}}, ({O_{\mathbf{t}}}_0, {O_{\mathbf{t}}}_1, ...), O_{\mathbf{d}}) \qquad \text{(28)}
```

<span id="eq-29"></span>

```math
O_{\mathrm{a}} \in \mathbb{B}_{20} \quad \wedge \quad \forall x \in O_{\mathbf{t}}: x \in \mathbb{B}_{32} \quad \wedge \quad O_{\mathbf{d}} \in \mathbb{B} \qquad \text{(29)}
```

ログ項目を単一の256バイト・ハッシュへ縮約するBloomフィルタ関数 $`M`$ を次のように定義する。

<span id="eq-30"></span>

```math
M(O) \equiv \bigvee_{x \in \{O_{\mathrm{a}}\} \cup O_{\mathbf{t}}} \big( M_{3:2048}(x) \big) \qquad \text{(30)}
```

ここで $`M_{3:2048}`$ は、任意のバイト列を受け取り2048ビット中の3ビットを設定する専用Bloomフィルタである。これは、バイト列のKeccak-256ハッシュについて、先頭から三つの各2バイト対の下位11ビットを取ることで行われる。[^8] 形式的には次のとおりである。

<span id="eq-31"></span><span id="eq-32"></span><span id="eq-33"></span><span id="eq-34"></span>

```math
\begin{aligned}
M_{3:2048}(\mathbf{x}: \mathbf{x} \in \mathbb{B}) & \equiv & \mathbf{y}: \mathbf{y} \in \mathbb{B}_{256} \quad \text{where:} & \qquad \text{(31)} \\
\mathbf{y} & = & (0, 0, ..., 0) \quad \text{except:} & \qquad \text{(32)} \\
\forall i \in \{0, 2, 4\}&:&\mathcal{B}_{2047 - m(\mathbf{x}, i)}(\mathbf{y}) = 1 & \qquad \text{(33)} \\
m(\mathbf{x}, i) &\equiv& \mathtt{KEC}(\mathbf{x})[i, i + 1] \bmod 2048 & \qquad \text{(34)}
\end{aligned}
```

ここで $`\mathcal{B}`$ はビット参照関数であり、 $`\mathcal{B}_{\mathrm{j}}(\mathbf{x})`$ はバイト配列 $`\mathbf{x}`$ のインデックス $`j`$ （0始まり）のビットに等しい。特に、これは $`\mathbf{x}`$ をビッグエンディアンとして扱う（上位ビットほど小さいインデックスを持つ）。

### 4.4.2. 全体的妥当性

ブロックが妥当であるのは、次の諸条件を満たす場合、かつその場合に限る。ブロックのommerフィールド $`B_{\mathbf{U}}`$ は空配列でなければならず、ブロック・ヘッダは与えられたトランザクション $`B_{\mathbf{T}}`$ および引き出し $`B_{\mathbf{W}}`$ と整合しなければならない。ヘッダがトランザクション $`B_{\mathbf{T}}`$ および引き出し $`B_{\mathbf{W}}`$ と整合するには、**stateRoot** ( $`H_{\mathrm{r}}`$ ) が基底状態 $`\boldsymbol{\sigma}`$ 上で全トランザクション、次いで全引き出しを順に実行した結果の状態（[第12節](#ch:finalisation)で規定）と一致しなければならない。また、**transactionsRoot** ( $`H_{\mathrm{t}}`$ )、**receiptsRoot** ( $`H_{\mathrm{e}}`$ )、**logsBloom** ( $`H_{\mathrm{b}}`$ )、**withdrawalsRoot** ( $`H_{\mathrm{w}}`$ ) は、それぞれトランザクション自体、実行から得られるトランザクション・レシート、結果のログ、および引き出しから正しく導出されなければならない。

<span id="eq-35"></span><span id="Receipts_Root_H__e"></span>

```math
\begin{aligned}
B_{\mathbf{U}} &\equiv () && \wedge \\
H_{\mathrm{r}} &\equiv \mathtt{TRIE}(L_S(\Pi(\boldsymbol{\sigma}, B))) && \wedge \\
H_{\mathrm{t}} &\equiv \mathtt{TRIE}\big(\{\forall i < \lVert B_{\mathbf{T}} \rVert,
  i \in \mathbb{N}: p_{\mathrm{T}}(i, B_{\mathbf{T}}[i])\}\big) && \wedge \\
H_{\mathrm{e}} &\equiv \mathtt{TRIE}\big(\{\forall i < \lVert B_{\mathbf{R}} \rVert,
  i \in \mathbb{N}: p_{\mathrm{R}}(i, B_{\mathbf{R}}[i])\}\big) && \wedge \\
H_{\mathrm{w}} &\equiv \mathtt{TRIE}\big(\{\forall i < \lVert B_{\mathbf{W}} \rVert,
  i \in \mathbb{N}: p_{\mathrm{W}}(i, B_{\mathbf{W}}[i])\}\big) && \wedge \\
H_{\mathrm{b}} &\equiv \bigvee_{\mathbf{r} \in B_{\mathbf{R}}} \big(\mathbf{r}_{\mathrm{b}}\big)
\end{aligned} \qquad \text{(35)}
```

ここで $`p_{\mathrm{W}}(k, v)`$ は引き出しに対するペア単位のRLP変換である。

<span id="eq-36"></span>

```math
p_{\mathrm{W}}(k, W) \equiv \left( \mathtt{RLP}(k), \mathtt{RLP}(L_{\mathrm{W}}(W)) \right) \qquad \text{(36)}
```

同様に、 $`p_{\mathrm{T}}(k, v)`$ と $`p_{\mathrm{R}}(k, v)`$ もペア単位のRLP変換であるが、EIP-2718トランザクションを特別に扱う。

<span id="eq-37"></span>

```math
p_{\mathrm{T}}(k, T) \equiv \left( \mathtt{RLP}(k), \begin{cases}
\mathtt{RLP}(L_{\mathrm{T}}(T)) & \text{if} \quad T_{\mathrm{x}} = 0 \\
(T_{\mathrm{x}}) \cdot \mathtt{RLP}(L_{\mathrm{T}}(T)) & \text{otherwise}
\end{cases}
\right) \qquad \text{(37)}
```

また、

<span id="eq-38"></span>

```math
p_{\mathrm{R}}(k, R) \equiv \left( \mathtt{RLP}(k), \begin{cases}
\mathtt{RLP}(L_{\mathrm{R}}(R)) & \text{if} \quad R_{\mathrm{x}} = 0 \\
(R_{\mathrm{x}}) \cdot \mathtt{RLP}(L_{\mathrm{R}}(R)) & \text{otherwise}
\end{cases}
\right) \qquad \text{(38)}
```

（ $`\cdot`$ はバイト配列の連結である）。

さらに、次が成り立つ。

<span id="eq-39"></span>

```math
\mathtt{TRIE}(L_{\mathrm{S}}(\boldsymbol{\sigma})) = {P(B_H)_H}_{\mathrm{r}} \qquad \text{(39)}
```

したがって $`\texttt{TRIE}(L_{\mathrm{S}}(\boldsymbol{\sigma}))`$ は、値をRLPで符号化した状態 $`\boldsymbol{\sigma}`$ のキー／値ペアを含むMerkle Patricia木構造のルート・ノード・ハッシュである。また $`P(B_{\mathrm{H}})`$ は、直接定義される $`B`$ の親ブロックである。

トランザクション計算から生じる値、特に[トランザクション・レシート](#Transaction_Receipt) $`B_{\mathbf{R}}`$ と、トランザクションの[状態累積関数 $`\Pi`$](#Pi) によって定義される値は、後の[第12.3節](#sec:statenoncevalidation)で形式化する。

### 4.4.3. 直列化

<div id="block_preparation_function_for_RLP_serialization_L__B">

</div>

<span id="block_preparation_function_for_RLP_serialization_L__H"></span>関数 $`L_{\mathrm{B}}`$ と $`L_{\mathrm{H}}`$ は、それぞれブロックおよびブロック・ヘッダの準備関数である。RLP変換が必要な場合の構造の型と順序を次のように規定する。

<span id="eq-40"></span><span id="eq-41"></span>

```math
\begin{aligned}
L_{\mathrm{H}}(H) &\equiv \big(H_{\mathrm{p}}, H_{\mathrm{o}}, H_{\mathrm{c}}, H_{\mathrm{r}}, H_{\mathrm{t}}, H_{\mathrm{e}}, H_{\mathrm{b}}, H_{\mathrm{d}},
  H_{\mathrm{i}}, H_{\mathrm{l}}, H_{\mathrm{g}}, H_{\mathrm{s}}, H_{\mathrm{x}}, H_{\mathrm{a}}, H_{\mathrm{n}}, H_{\mathrm{f}}, H_{\mathrm{w}}\big)
  \qquad \text{(40)} \\
L_{\mathrm{B}}(B) &\equiv \big(L_{\mathrm{H}}(B_{\mathrm{H}}), \widetilde{L}_{\mathrm{T}}^{*}(B_{\mathbf{T}}),
  L_{\mathrm{H}}^{*}(B_{\mathbf{U}}), L_{\mathrm{W}}^{*}(B_{\mathbf{W}})\big) \qquad \text{(41)}
\end{aligned}
```

ここで $`\widetilde{L}_{\mathrm{T}}`$ はEIP-2718トランザクションを特別に扱う。

<span id="eq-42"></span>

```math
\widetilde{L}_{\mathrm{T}}(T) = \begin{cases}
L_{\mathrm{T}}(T) & \text{if} \quad T_{\mathrm{x}} = 0 \\
(T_{\mathrm{x}}) \cdot \mathtt{RLP}(L_{\mathrm{T}}(T)) & \text{otherwise}
\end{cases} \qquad \text{(42)}
```

<span id="general_element_wise_sequence_transformation_f_pow_asterisk"></span> $`\widetilde{L}_{\mathrm{T}}^{*}`$ 、 $`L_{\mathrm{H}}^{*}`$ 、 $`L_{\mathrm{W}}^{*}`$ は要素単位の列変換であり、次のとおりである。

<span id="eq-43"></span>

```math
f^{*}\big( (x_0, x_1, ...) \big) \equiv \big( f(x_0), f(x_1), ... \big) \quad \text{（任意の関数 } f \text{ について）} \qquad \text{(43)}
```

構成要素の型を次のように定義する。

<span id="eq-44"></span>

```math
\begin{array}{lclclcl}
H_{\mathrm{p}} \in \mathbb{B}_{32} & \wedge & H_{\mathrm{o}} \in \mathbb{B}_{32} & \wedge & H_{\mathrm{c}} \in \mathbb{B}_{20} & \wedge \\
H_{\mathrm{r}} \in \mathbb{B}_{32} & \wedge & H_{\mathrm{t}} \in \mathbb{B}_{32} & \wedge & H_{\mathrm{e}} \in \mathbb{B}_{32} & \wedge \\
H_{\mathrm{b}} \in \mathbb{B}_{256} & \wedge & H_{\mathrm{d}} \in \mathbb{N} & \wedge & H_{\mathrm{i}} \in \mathbb{N} & \wedge \\
H_{\mathrm{l}} \in \mathbb{N} & \wedge & H_{\mathrm{g}} \in \mathbb{N} & \wedge & H_{\mathrm{s}} \in \mathbb{N}_{256} & \wedge \\
H_{\mathrm{x}} \in \mathbb{B} & \wedge & H_{\mathrm{a}} \in \mathbb{B}_{32} & \wedge & H_{\mathrm{n}} \in \mathbb{B}_{8} & \wedge \\
H_{\mathrm{f}} \in \mathbb{N} & \wedge & H_{\mathrm{w}} \in \mathbb{B}_{32}
\end{array} \qquad \text{(44)}
```

ここで、

<span id="eq-45"></span>

```math
\mathbb{B}_{\mathrm{n}} = \{ B: B \in \mathbb{B} \wedge \lVert B \rVert = n \} \qquad \text{(45)}
```

である。

以上で、形式的なブロック構造を構成する厳密な仕様が得られた。RLP関数 $`\texttt{RLP}`$ （[付録B](#app:rlp)参照）は、この構造をネットワーク送信またはローカル保存が可能なバイト列へ変換する正準な方法を与える。

### 4.4.4. ブロック・ヘッダの妥当性

$`P(B_{\mathrm{H}})`$ を $`B`$ の親ブロックとして、形式的に次のように定義する。

<span id="eq-46"></span>

```math
P(H) \equiv B': \mathtt{KEC}(\mathtt{RLP}(B'_{\mathrm{H}})) = H_{\mathrm{p}} \qquad \text{(46)}
```

<div id="block_number_H__i">

</div>

ブロック番号は親のブロック番号に1を加えたものである。

<span id="eq-47"></span>

```math
H_{\mathrm{i}} \equiv {{P(H)_{\mathrm{H}}}_{\mathrm{i}}} + 1 \qquad \text{(47)}
```

<span id="H__f"></span>

*London* リリースでは、ブロック属性*gas当たり基本手数料* [$`H_{\mathrm{f}}`$](#block_baseFeePerGas_H__f) が導入された（[(Buterin et al. 2019)](#ref-EIP-1559)によるEIP-1559を参照）。基本手数料とは、ブロック内のトランザクション実行中に消費されるgas 1単位当たりにバーンされるwei量である。その値は、親ブロックが使用したgasと親ブロックの*gas目標値*との差の関数である。

gas当たりの期待基本手数料を $`F(H)`$ として次のように定義する。

<span id="eq-48"></span>

```math
F(H) \equiv \begin{cases}
    1000000000  & \text{if} \quad H_{\mathrm{i}} = F_{\mathrm{London}} \\
    {P(H)_{\mathrm{H}}}_{\mathrm{f}}  & \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} = \tau \\
    {P(H)_{\mathrm{H}}}_{\mathrm{f}} - \nu & \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} < \tau \\
    {P(H)_{\mathrm{H}}}_{\mathrm{f}} + \nu & \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} > \tau
  \end{cases} \qquad \text{(48)}
```

ここで、

<span id="eq-49"></span><span id="eq-50"></span><span id="eq-51"></span><span id="eq-52"></span><span id="eq-53"></span>

```math
\begin{aligned}
\tau &\equiv \lfloor\frac{{P(H)_{\mathrm{H}}}_{\mathrm{l}}}{\rho} \rfloor & \qquad \text{(49)} \\
\rho &\equiv 2 & \qquad \text{(50)} \\
\nu^{*} &\equiv \begin{cases}
      \lfloor \frac{{P(H)_{\mathrm{H}}}_{\mathrm{f}} \times ({\tau - P(H)_{\mathrm{H}}}_{\mathrm{g}})}{\tau} \rfloor &  \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} < \tau \\
      \lfloor \frac{{P(H)_{\mathrm{H}}}_{\mathrm{f}} \times ({P(H)_{\mathrm{H}}}_{\mathrm{g}} - \tau)}{\tau} \rfloor &  \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} > \tau \\
  \end{cases} & \qquad \text{(51)} \\
\nu &\equiv \begin{cases}
    \lfloor \frac{\nu^*}{\xi} \rfloor &  \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} < \tau \\
    max(\lfloor \frac{\nu^*}{\xi} \rfloor, 1) &  \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} > \tau \\
  \end{cases} & \qquad \text{(52)} \\
\xi &\equiv 8 & \qquad \text{(53)}
\end{aligned}
```

*gas目標値* $`\tau`$ は、gas上限 $`H_{\mathrm{l}}`$ を、2に設定された大域定数である*弾力性乗数* $`\rho`$ で割った値として定義される。したがって、各ブロックはgas上限までgasを消費できる一方、平均的にはブロックがgas目標値相当のgasを消費するよう基本手数料が調整される。親ブロックのgas使用量がgas目標値を超える場合、現在のブロックでは基本手数料が引き上げられ、反対に親ブロックのgas使用量がgas目標値を下回る場合は引き下げられる。

基本手数料の増減幅 $`\nu`$ は、親ブロックが消費したgas量と親ブロックのgas目標値との差に比例する。基本手数料への影響は、*基本手数料最大変化分母*と呼ばれる大域定数（形式的には $`\xi`$ ）によって抑制され、その値は8に設定される。値が8であるため、基本手数料が一つのブロックから次のブロックまでに増減できる割合は最大12.5%となる。

<span id="tnref-3"></span>[訳注3](#tn-3)

<div id="block_gas_limit_H__l">

</div>

ヘッダ $`H`$ を持つブロックの正準gas上限 $`H_{\mathrm{l}}`$ は、次の関係を満たさなければならない。

<span id="eq-54"></span>

```math
\begin{aligned}
& & H_{\mathrm{l}} < {P(H)_{\mathrm{H}}}_{\mathrm{l}'} + \left\lfloor\frac{{P(H)_{\mathrm{H}}}_{\mathrm{l}'}}{1024}\right\rfloor \quad \wedge & \qquad \text{(54)} \\
& & H_{\mathrm{l}} > {P(H)_{\mathrm{H}}}_{\mathrm{l}'} - \left\lfloor\frac{{P(H)_{\mathrm{H}}}_{\mathrm{l}'}}{1024}\right\rfloor \quad \wedge \\
& & H_{\mathrm{l}} \geqslant 5000
\end{aligned}
```

ここで、

<span id="eq-55"></span>

```math
\begin{aligned}
{P(H)_{\mathrm{H}}}_{\mathrm{l}'} &\equiv \begin{cases}
      {P(H)_{\mathrm{H}}}_{\mathrm{l}} \times \rho &  \text{if} \quad H_{\mathrm{i}} = F_{\mathrm{London}} \\
      {P(H)_{\mathrm{H}}}_{\mathrm{l}} &  \text{if} \quad H_{\mathrm{i}} > F_{\mathrm{London}} \\
  \end{cases} & \qquad \text{(55)}
\end{aligned}
```

gas使用量の不連続を避けるため、現在のブロックのgas上限を検証する際に用いる親ブロックのgas上限値は、*London* フォーク・ブロックにおいて*弾力性乗数* $`\rho`$ を掛けることで修正される。この修正後の値を $`{P(H)_{\mathrm{H}}}_{\mathrm{l}'}`$ と呼ぶ。これにより、*London* 後のブロックのgas目標値を、*London* 前のブロックのgas上限とおおむね同水準に設定できる。

<div id="block_timestamp_H__s">

</div>

$`H_{\mathrm{s}}`$ はブロック $`H`$ のタイムスタンプ（Unix時刻）であり、次の関係を満たさなければならない。

<span id="eq-56"></span>

```math
H_{\mathrm{s}} > {P(H)_{\mathrm{H}}}_{\mathrm{s}} \qquad \text{(56)}
```

*Paris* ハードフォークはEthereumの合意方式をプルーフ・オブ・ワークからプルーフ・オブ・ステークへ変更し、その結果、プルーフ・オブ・ワークに関係する多数のブロック・ヘッダ属性が非推奨となった。これには **nonce** ( $`H_{\mathbf{n}}`$ )、**ommersHash** ( $`H_{\mathbf{o}}`$ )、**difficulty** ( $`H_{\mathbf{d}}`$ )、**mixHash** ( $`H_{\mathbf{m}}`$ ) が含まれる。

**mixHash** は新たなフィールド **prevRandao** ( $`H_{\mathbf{a}}`$ ) に置き換えられた。プルーフ・オブ・ワークに関係するほかのヘッダ・フィールドは、次の定数に置き換えられた。

<span id="eq-57"></span><span id="eq-58"></span><span id="eq-59"></span>

```math
\begin{aligned}
H_{\mathrm{o}} & \equiv & \texttt{KEC}(\texttt{RLP}(())) & \qquad \text{(57)} \\
H_{\mathrm{d}} & \equiv  & 0 & \qquad \text{(58)} \\
H_{\mathrm{n}}  & \equiv & \texttt{0x0000000000000000} & \qquad \text{(59)}
\end{aligned}
```

**prevRandao** の値はBeacon Chainの情報を用いて決定しなければならない。Beacon Chain上で *RANDAO* 値を生成する詳細は本稿の範囲外であるが、直前のブロックについて期待される *RANDAO* 値を $`\mathtt{PREVRANDAO}()`$ と表す。

<div id="block_header_validity_function">

</div>

以上により、ブロック・ヘッダ妥当性関数 $`V(H)`$ を次のように定義できる。

<span id="eq-60"></span>

```math
\begin{aligned}
V(H) & \equiv & H_{\mathrm{g}} \le H_{\mathrm{l}}  \quad \wedge & \qquad \text{(60)} \\
& & H_{\mathrm{l}} < {P(H)_{\mathrm{H}}}_{\mathrm{l}'} + \left\lfloor\frac{{P(H)_{\mathrm{H}}}_{\mathrm{l}'}}{1024}\right\rfloor  \quad \wedge \\
& & H_{\mathrm{l}} > {P(H)_{\mathrm{H}}}_{\mathrm{l}'} - \left\lfloor\frac{{P(H)_{\mathrm{H}}}_{\mathrm{l}'}}{1024}\right\rfloor  \quad \wedge \\
& & H_{\mathrm{l}} \geqslant 5000  \quad \wedge \\
& & H_{\mathrm{s}} > {P(H)_{\mathrm{H}}}_{\mathrm{s}} \quad \wedge \\
& & H_{\mathrm{i}} = {P(H)_{\mathrm{H}}}_{\mathrm{i}} +1 \quad \wedge \\
& & \lVert H_{\mathrm{x}} \rVert \le 32 \quad \wedge \\
& & H_{\mathrm{f}} = F(H) \wedge \\
& & H_{\mathrm{o}} = \texttt{KEC}(\texttt{RLP}(())) \quad \wedge \\
& & H_{\mathrm{d}} = 0 \quad \wedge \\
& & H_{\mathrm{n}} = \texttt{0x0000000000000000} \quad \wedge \\
& & H_{\mathrm{a}} = \mathtt{PREVRANDAO}()
\end{aligned}
```

さらに、**extraData** は最大32バイトでなければならない。

<span id="ch:payment"></span>

# 5. Gas と支払い

ネットワークの悪用という問題を避け、チューリング完全性から必然的に生じる問題を回避するため、Ethereum におけるプログラム可能な計算はすべて有料である。手数料表は *gas* 単位で規定される（各種計算に伴う手数料は[付録G](#app:fees)を参照）。したがって、プログラム可能な計算の各断片（コントラクトの作成、メッセージ呼び出し、アカウント・ストレージの使用とアクセス、仮想マシン上の演算実行を含む）には、gas で表した普遍的に合意されたコストがある。

すべてのトランザクションには、特定量の gas、すなわち **gasLimit** が関連付けられる。これは送信者のアカウント残高から暗黙に購入される gas 量である。購入は[第6節](#ch:transactions)で定義する*実効 gas 価格*で行われる。アカウント残高がこの購入を賄えない場合、トランザクションは無効とみなされる。トランザクション終了時の未使用 gas は（購入時と同じレートで）送信者のアカウントへ払い戻されるため、**gasLimit** と呼ぶ。gas はトランザクションの実行外には存在しない。したがって、信頼できるコードが関連付けられたアカウントには、比較的高い gas 上限を設定したままにできる。

*London* ハードフォークで [(Buterin et al. 2019)](#ref-EIP-1559) の EIP-1559 が導入されて以来、ブロックに含まれる各トランザクションは*基本手数料*を支払わなければならない。基本手数料は消費 gas 1単位当たりの Wei で指定され、一つのブロック内の各トランザクションについて一定である。基本手数料を満たすために支払われた Ether はバーンされる（流通から除かれる）。基本手数料は、前ブロックの gas 消費量とその *gas 目標値*との関係を関数として動的に調整される。gas 目標値は現在、ブロックの gas 上限の半分であり、この上限はバリデータが調整できる。前ブロックの総 gas 消費量が gas 目標値を超える場合、現在の基本手数料におけるブロック空間の需要超過を示すため、基本手数料を引き上げる。反対に、前ブロックの gas 消費量が gas 目標値を下回る場合、現在の基本手数料におけるブロック空間の需要は gas 目標値を下回っており、したがって基本手数料を引き下げる。この調整によって、平均的なブロックの gas 消費量は gas 目標値に揃うはずである。基本手数料の設定方法の詳細は[第4.4節](#subsec:The_Block)を参照されたい。

バリデータにトランザクション収録のインセンティブを与えるため、*優先手数料*と呼ばれる追加手数料があり、これも消費 gas 1単位当たりの Wei で指定される。したがって、トランザクション送信者が支払う総手数料は、gas 当たり基本手数料と gas 当たり優先手数料の和に、総消費 gas を乗じたものである。優先手数料を満たす Ether は、通常バリデータの管理下にあるアカウントのアドレスである*受益者*アドレスへ送られる。

型2トランザクションを使用するトランザクション送信者は、支払ってもよい最大優先手数料（**maxPriorityFeePerGas**）と、優先手数料・基本手数料の両方を含めて支払ってもよい最大総手数料（**maxFeePerGas**）を指定できる。そのトランザクションがブロックに収録されるには、**maxFeePerGas** が基本手数料以上でなければならない。型0および型1のトランザクションには gas 価格を指定するフィールドが **gasPrice** の一つだけあり、これもブロックに収録されるには基本手数料以上でなければならない。型0または型1のトランザクションでは、**gasPrice** が基本手数料を上回る額が優先手数料となる。

トランザクション送信者は任意の優先手数料を選べるが、バリデータも任意のトランザクションを無視できる。したがって、優先手数料が高いトランザクションは送信者により多くの Ether を負担させ、バリデータにより大きな価値をもたらすため、収録対象として選ばれやすい。許容可能な最低優先手数料には重み付き分布が生じるため、トランザクション送信者は優先手数料を下げることと、自分のトランザクションが適時にブロックに収録される可能性を最大にすることとの間で、必然的にトレードオフを選ばなければならない。

<span id="ch:transactions"></span>

# 6. トランザクションの実行

トランザクションの実行は Ethereum プロトコルで最も複雑な部分であり、状態遷移関数 [$`\Upsilon`$](#Upsilon_state_transition) を定義する。実行されるトランザクションは、まず次の内在的妥当性検査に合格すると仮定する。

1.  トランザクションが整形式の RLP であり、末尾に余分なバイトがない。

2.  トランザクション署名が妥当である。

3.  [トランザクション nonce](#transaction_nonce) が妥当である（[送信者アカウントの現在の nonce](#account_nonce) と等しい）。

4.  送信者アカウントにコントラクト・コードがデプロイされていない（[(Feist, Khovratovich, and Wijden 2021)](#ref-EIP-3607) の EIP-3607 参照）。

5.  gas 上限が、トランザクションの使用する固有gas $`g_0`$ 以上である。

6.  送信者のアカウント残高が、前払いに必要なコスト $`v_0`$ 以上である。

7.  型2では **maxFeePerGas** $`T_m`$ 、型0および型1では **gasPrice** $`T_p`$ が、ブロックの基本手数料 $`H_{\mathrm{f}}`$ 以上である。

8.  型2では **maxPriorityFeePerGas** $`T_f`$ が **maxFeePerGas** $`T_m`$ 以下である。

形式的には、 $`T`$ をトランザクション、 $`\boldsymbol{\sigma}`$ を状態として、関数 [$`\Upsilon`$](#Upsilon_state_transition) を考える。

<span id="eq-61"></span>

```math
\boldsymbol{\sigma}' = \Upsilon(\boldsymbol{\sigma}, T) \qquad \text{(61)}
```

したがって $`\boldsymbol{\sigma}'`$ はトランザクション後の状態である。また、[$`\Upsilon^{\mathrm{g}}`$](#tx_total_gas_used_Upsilon_pow_g) を実行で使用した gas 量、[$`\Upsilon^{\mathbf{l}}`$](#tx_logs_Upsilon_pow_l) を累積ログ項目、[$`\Upsilon^{\mathrm{z}}`$](#tx_status_Upsilon_pow_z) を結果のステータス・コードと定義する。これらは後で形式的に定義する。

<span id="ch:substate"></span>

## 6.1. サブ状態

トランザクションの実行中には、トランザクション直後に処理される一定の情報を蓄積する。これを*累積トランザクション・サブ状態*、略して*累積サブ状態*と呼び、タプル $`A`$ として表す。

<span id="eq-62"></span>

```math
A \equiv (A_{\mathbf{s}}, A_{\mathbf{l}}, A_{\mathbf{t}}, A_{\mathrm{r}}, A_{\mathbf{a}}, A_{\mathbf{K}}) \qquad \text{(62)}
```

<div id="self_destruct_set_wordy_defn_A__s">

</div>

このタプルには、自己破棄集合 $`A_{\mathbf{s}}`$ 、すなわちトランザクション完了後に破棄されるアカウントの集合が含まれる。<span id="tx_log_series_wordy_defn_A__l"></span> $`A_{\mathbf{l}}`$ はログ列である。これはVMコード実行中に保存され索引付け可能な「チェックポイント」の列であり、分散型アプリケーションのフロントエンドなどEthereum世界の外部にいる観察者がコントラクト呼び出しを容易に追跡できるようにする。<span id="tx_touched_accounts_wordy_defn_A__t"></span> $`A_{\mathbf{t}}`$ は接触済みアカウントの集合であり、そのうち空のものはトランザクション終了時に削除される。<span id="refund_balance_defn_words_A__r"></span> $`A_{\mathrm{r}}`$ は還付残高であり、[SSTORE](#SSTORE)命令を使用してコントラクト・ストレージを非ゼロ値からゼロへ戻すと増加する。直ちに還付されるわけではないが、総実行コストの一部を相殺できる。最後に、[(Buterin and Swende 2020a)](#ref-EIP-2929)によるEIP-2929は、<span id="accessed_addresses_defn_words_A__a"></span>アクセス済みアカウント・アドレス集合 $`A_{\mathbf{a}}`$ と、<span id="accessed_storage_keys_defn_words_A__k"></span>アクセス済みストレージ・キー集合 $`A_{\mathbf{K}}`$ を導入した（より正確には、 $`A_{\mathbf{K}}`$ の各要素は20バイトのアカウント・アドレスと32バイトのストレージ・スロットからなるタプルである）。

空の累積サブ状態 $`A^0`$ は、自己破棄、ログ、接触済みアカウント、アクセス済みストレージを持たず、還付残高がゼロで、アクセス済みアドレスにすべてのプリコンパイル済みコントラクトを含むものとして定義する。

<span id="eq-63"></span>

```math
A^0 \equiv (\varnothing, (), \varnothing, 0, \pi, \varnothing) \qquad \text{(63)}
```

ここで $`\pi`$ はすべてのプリコンパイル済みアドレスの集合である。

## 6.2. 実行

<div id="intrinsic_gas_g_0">

</div>

固有gas $`g_0`$ 、すなわちこのトランザクションが実行前に支払う必要のあるgas量を次のように定義する。

<span id="eq-64"></span>

```math
\begin{aligned}
g_0 \equiv {} & \sum_{i \in T_{\mathbf{i}}, T_{\mathbf{d}}} \begin{cases} G_{\mathrm{txdatazero}} & \text{if} \quad i = 0 \\ G_{\mathrm{txdatanonzero}} & \text{otherwise} \end{cases} & \qquad \text{(64)} \\
{} & + \begin{cases} G_{\mathrm{txcreate}} + R({\lVert T_{\mathbf{i}} \rVert}) & \text{if} \quad T_{\mathrm{t}} = \varnothing \\ 0 & \text{otherwise} \end{cases} \\
{} & + G_{\mathrm{transaction}} \\
{} & + \sum_{j = 0}^{\lVert T_{\mathbf{A}} \rVert - 1} \big( G_{\mathrm{accesslistaddress}} + \lVert T_{\mathbf{A}}[j]_{\mathbf{s}} \rVert G_{\mathrm{accessliststorage}} \big)
\end{aligned}
```

ここで $`T_{\mathbf{i}},T_{\mathbf{d}}`$ は、トランザクションがコントラクト作成かメッセージ呼び出しかに応じて、その関連データまたは初期化EVMコードのバイト列を意味する。トランザクションがコントラクトを作成する場合は $`G_{\mathrm{txcreate}}`$ を加えるが、メッセージ呼び出しの場合は加えない。 $`G_{\mathrm{accesslistaddress}}`$ と $`G_{\mathrm{accessliststorage}}`$ は、それぞれアカウントおよびストレージへのアクセスをウォーム化するコストである。 $`G`$ は[付録G](#app:fees)で完全に定義する。

<div id="initcode_cost">

</div>

*initcode コスト関数* $`R`$ を、新しいコントラクトの作成コードを実行する前に initcode の各ワードについて支払う必要がある gas 量として定義する。

<span id="eq-65"></span>

```math
R(x) \equiv G_{\mathrm{initcodeword}} \times \lceil \frac{x}{32} \rceil \qquad \text{(65)}
```

<div id="effective_gas_price_p">

</div>

*実効 gas 価格* $`p`$ を、トランザクション実行中に消費した gas 1単位当たりに署名者が支払う Wei の量として定義する。次のように計算する。

<span id="eq-66"></span>

```math
p \equiv \begin{cases}
  T_{\mathrm{p}} & \text{if} \; T_{\mathrm{x}} = 0 \lor T_{\mathrm{x}} = 1 \\
  f + H_{\mathrm{f}} & \text{if} \; T_{\mathrm{x}} = 2 \\
  \end{cases} \qquad \text{(66)}
```

<div id="priority_fee_f">

</div>

ここで $`f`$ は*優先手数料*、すなわち実行中に消費した gas 1単位当たりにブロックの受益者アドレスが受け取る Wei の量である。次のように計算する。

<span id="eq-67"></span>

```math
f \equiv \begin{cases}
  T_{\mathrm{p}} - H_{\mathrm{f}} & \text{if} \; T_{\mathrm{x}} = 0 \lor T_{\mathrm{x}} = 1 \\
  min(T_{\mathrm{f}}, T_{\mathrm{m}} - H_{\mathrm{f}}) & \text{if} \; T_{\mathrm{x}} = 2 \\
  \end{cases} \qquad \text{(67)}
```

前払いコスト $`v_0`$ は次のように計算される。

<span id="eq-68"></span>

```math
v_0 \equiv \begin{cases}
  T_{\mathrm{g}}T_{\mathrm{p}} + T_{\mathrm{v}} & \text{if} \; T_{\mathrm{x}} = 0 \lor T_{\mathrm{x}} = 1 \\
  T_{\mathrm{g}}T_{\mathrm{m}} + T_{\mathrm{v}} & \text{if} \; T_{\mathrm{x}} = 2 \\
  \end{cases} \qquad \text{(68)}
```

妥当性は次のように判定される。

<span id="eq-69"></span><span id="transaction_nonce"></span>

```math
\begin{array}{rcl}
S(T) & \neq & \varnothing \quad \wedge \\
\boldsymbol{\sigma}[S(T)]_{\mathrm{c}} & = & \texttt{KEC}\big( () \big) \quad \wedge \\
T_{\mathrm{n}} & = & \boldsymbol{\sigma}[S(T)]_{\mathrm{n}} \quad \wedge \\
g_0 & \leqslant & T_{\mathrm{g}} \quad \wedge \\
v_0 & \leqslant & \boldsymbol{\sigma}[S(T)]_{\mathrm{b}} \quad \wedge \\
m & \geqslant & H_{\mathrm{f}} \quad \wedge \\
n & \leqslant & 49152 \quad \wedge \\
T_{\mathrm{g}} & \leqslant & {B_{\mathrm{H}}}_{\mathrm{l}} - \ell(B_{\mathbf{R}})_{\mathrm{u}}
\end{array} \qquad \text{(69)}
```

ここで、

<span id="eq-70"></span>

```math
m \equiv \begin{cases}
  T_{\mathrm{p}} & \text{if} \; T_{\mathrm{x}} = 0 \lor T_{\mathrm{x}} = 1 \\
  T_{\mathrm{m}} & \text{if} \; T_{\mathrm{x}} = 2 \\
  \end{cases} \qquad \text{(70)}
```

かつ、

<span id="eq-71"></span>

```math
n \equiv \begin{cases}
    \lVert T_{\mathrm{i}} \rVert & \text{if} \; T_{\mathrm{t}} = \varnothing \\
    0 & \text{otherwise}
  \end{cases} \qquad \text{(71)}
```

最後から二番目の条件は、作成トランザクションについてinitcodeの長さが49152バイト以下であることを保証する。最後の条件にも注意されたい。トランザクションのgas上限 $`T_{\mathrm{g}}`$ と、それ以前にこのブロックで使用されたgas $`\ell(B_{\mathbf{R}})_{\mathrm{u}}`$ の和は、ブロックの **gasLimit** $`{B_{\mathrm{H}}}_{\mathrm{l}}`$ 以下でなければならない。また、記法をわずかに濫用して、 $`\boldsymbol{\sigma}[S(T)] = \varnothing`$ の場合には $`\boldsymbol{\sigma}[S(T)]_{\mathrm{c}} = \texttt{KEC}\big( () \big)`$ 、 $`\boldsymbol{\sigma}[S(T)]_{\mathrm{n}} = 0`$ 、 $`\boldsymbol{\sigma}[S(T)]_{\mathrm{b}} = 0`$ と仮定する。

型2トランザクションについては、**maxPriorityFeePerGas** が **maxFeePerGas** 以下であるという追加検査を行う。

<span id="eq-72"></span>

```math
T_{\mathrm{m}} \geqslant T_{\mathrm{f}} \qquad \text{(72)}
```

妥当なトランザクションの実行は、状態への取消不能な変更から始まる。送信者アカウント $`S(T)`$ の[nonce](#account_nonce)を1増加させ、残高から前払いコストの一部 $`T_{\mathrm{g}} p`$ を減じる。後続の計算に利用できるgas $`g`$ は $`T_{\mathrm{g}} - g_0`$ と定義される。コントラクト作成かメッセージ呼び出しかを問わず、計算は最終的な状態（現在状態と同値でも正当である）をもたらす。この状態変更は決定論的であり、決して無効にはならない。この時点以降、無効なトランザクションは存在し得ない。

チェックポイント状態 $`\boldsymbol{\sigma}_0`$ を次のように定義する。

<span id="eq-73"></span><span id="eq-74"></span><span id="eq-75"></span>

```math
\begin{aligned}
\boldsymbol{\sigma}_0 & \equiv & \boldsymbol{\sigma} \quad \text{except:} & \qquad \text{(73)} \\
\boldsymbol{\sigma}_0[S(T)]_{\mathrm{b}} & \equiv & \boldsymbol{\sigma}[S(T)]_{\mathrm{b}} - T_{\mathrm{g}} p & \qquad \text{(74)} \\
\boldsymbol{\sigma}_0[S(T)]_{\mathrm{n}} & \equiv & \boldsymbol{\sigma}[S(T)]_{\mathrm{n}} + 1 & \qquad \text{(75)}
\end{aligned}
```

$`\boldsymbol{\sigma}_0`$ から $`\boldsymbol{\sigma}_{\mathrm{P}}`$ を評価する方法は、コントラクト作成かメッセージ呼び出しかというトランザクション型に依存する。実行後の暫定状態 $`\boldsymbol{\sigma}_{\mathrm{P}}`$ 、残存gas $`g'`$ 、累積サブ状態 $`A`$ 、ステータス・コード $`z`$ のタプルを次のように定義する。

<span id="eq-76"></span>

```math
(\boldsymbol{\sigma}_{\mathrm{P}}, g', A, z) \equiv \begin{cases}
\Lambda_{4}(\boldsymbol{\sigma}_0, A^{*}, S(T), S(T), g, &\\ \quad\; p, T_{\mathrm{v}}, T_{\mathbf{i}}, 0, \varnothing, \top) & \text{if} \quad T_{\mathrm{t}} = \varnothing \\
\Theta_{4}(\boldsymbol{\sigma}_0, A^{*}, S(T), S(T), T_{\mathrm{t}}, &\\ \quad\; T_{\mathrm{t}}, g, p, T_{\mathrm{v}}, T_{\mathrm{v}}, T_{\mathbf{d}}, 0, \top) & \text{otherwise}
\end{cases} \qquad \text{(76)}
```

ここで、

<span id="eq-77"></span><span id="eq-78"></span><span id="eq-79"></span><span id="eq-80"></span>

```math
\begin{aligned}
A^{*} & \equiv A^0 \quad \text{except} & \qquad \text{(77)} \\
A^{*}_{\mathbf{K}} & \equiv \bigcup_{E \in T_{\mathbf{A}}} \big\{ \forall i < \lVert E_{\mathbf{s}} \rVert, i \in \mathbb{N}: \; (E_{\mathrm{a}}, E_{\mathbf{s}}[i]) \big\} & \qquad \text{(78)} \\
A^{*}_{\mathbf{a}} & \equiv \begin{cases}
a \cup T_{\mathrm{t}} & \text{if} \quad T_{\mathrm{t}} \neq \varnothing \\
a & \text{otherwise}
\end{cases} & \qquad \text{(79)} \\
a & \equiv A^0_{\mathbf{a}} \cup S(T) \cup H_c \cup_{E \in T_{\mathbf{A}}} \{ E_{\mathrm{a}} \} & \qquad \text{(80)}
\end{aligned}
```

また $`g`$ は、トランザクションが存在するために支払う基本量を差し引いた後に残るgas量である。

<span id="eq-81"></span>

```math
g \equiv T_{\mathrm{g}} - g_0 \qquad \text{(81)}
```

$`\Theta_{4}`$ と $`\Lambda_{4}`$ は、関数値の最初の四つの構成要素だけを取ることを表すために用いている点に注意されたい。最後の構成要素はメッセージ呼び出しの出力値（バイト配列）を表し、トランザクション評価の文脈では使用されない。

次に、残存gas $`g'`$ と還付カウンタからの一定の割当てに基づき、元のレートで送信者へ還付する量 $`g^{*}`$ を決定して状態を最終化する。

<span id="eq-82"></span>

```math
g^{*} \equiv g' + \min \left\{ \Big\lfloor \dfrac{T_{\mathrm{g}} - g'}{5} \Big\rfloor, A_{\mathrm{r}} \right\} \qquad \text{(82)}
```

還付可能な総量は、正当に残ったgas $`g'`$ に [$`A_{\mathrm{r}}`$](#refund_balance_defn_words_A__r) を加えたものである。ただし後者は、総使用量 $`T_{\mathrm{g}} - g'`$ の最大5分の1[^9]（切り捨て）に制限される。したがって $`g^{*}`$ は、トランザクション実行後に残るgasの総量である。

現在のブロック $`B`$ の受益者としてアドレスが指定されたバリデータは、消費gas量に、この節で [$`f`$](#priority_fee_f) と定義するトランザクションの*gas当たり優先手数料*を掛けた額を受け取る。トランザクション送信者が支払うEtherのうち基本手数料に充てられる分は、そのアカウントから引き落とされるが、ほかのいかなるアカウントにも加算されないため、バーンされる。

最終化前状態 $`\boldsymbol{\sigma}^{*}`$ を暫定状態 $`\boldsymbol{\sigma}_{\mathrm{P}}`$ によって次のように定義する。

<span id="eq-83"></span><span id="eq-84"></span><span id="eq-85"></span>

```math
\begin{aligned}
\boldsymbol{\sigma}^{*} & \equiv & \boldsymbol{\sigma}_{\mathrm{P}} \quad \text{except} & \qquad \text{(83)} \\
\boldsymbol{\sigma}^{*}[S(T)]_{\mathrm{b}} & \equiv & \boldsymbol{\sigma}_{\mathrm{P}}[S(T)]_{\mathrm{b}} + g^{*} p & \qquad \text{(84)} \\
\boldsymbol{\sigma}^{*}[{B_{\mathrm{H}}}_{\mathrm{c}}]_{\mathrm{b}} & \equiv & \boldsymbol{\sigma}_{\mathrm{P}}[{B_{\mathrm{H}}}_{\mathrm{c}}]_{\mathrm{b}} + (T_{\mathrm{g}} - g^{*}) f & \qquad \text{(85)}
\end{aligned}
```

最終状態 $`\boldsymbol{\sigma}'`$ は、自己破棄集合に現れるか、接触済みかつ空であるすべてのアカウントを削除した後に得られる。

<span id="eq-86"></span><span id="eq-87"></span><span id="eq-88"></span>

```math
\begin{aligned}
\boldsymbol{\sigma}' & \equiv & \boldsymbol{\sigma}^{*} \quad \text{except} & \qquad \text{(86)} \\
\forall i \in A_{\mathbf{s}}: \boldsymbol{\sigma}'[i] & = & \varnothing & \qquad \text{(87)} \\
\forall i \in A_{\mathbf{t}}: \boldsymbol{\sigma}'[i] & = & \varnothing \quad\text{if}\quad \mathtt{DEAD}(\boldsymbol{\sigma}^{*}, i) & \qquad \text{(88)}
\end{aligned}
```

<div id="tx_total_gas_used_Upsilon_pow_g">

</div>

<span id="Upsilon_pow_l"></span>

<span id="tx_logs_Upsilon_pow_l"></span><span id="Upsilon_pow_z"></span>

<span id="tx_status_Upsilon_pow_z"></span>最後に、このトランザクションで使用された総gas $`\Upsilon^{\mathrm{g}}`$ 、このトランザクションが生成したログ $`\Upsilon^{\mathbf{l}}`$ 、およびトランザクションのステータス・コード $`\Upsilon^{\mathrm{z}}`$ を規定する。

<span id="eq-89"></span><span id="eq-90"></span><span id="eq-91"></span>

```math
\begin{aligned}
\Upsilon^{\mathrm{g}}(\boldsymbol{\sigma}, T) & \equiv & T_{\mathrm{g}} - g^{*} & \qquad \text{(89)} \\
\Upsilon^{\mathbf{l}}(\boldsymbol{\sigma}, T) & \equiv & A_{\mathbf{l}} & \qquad \text{(90)} \\
\Upsilon^{\mathrm{z}}(\boldsymbol{\sigma}, T) & \equiv & z & \qquad \text{(91)}
\end{aligned}
```

これらは[トランザクション・レシート](#Transaction_Receipt)の定義に用いられ、さらに[後で](#sigma_n)状態検証にも用いられる。

<span id="ch:create"></span>

# 7. コントラクト作成

<div id="endow">

</div>

アカウント作成にはいくつかの固有パラメータを用いる。送信者 $`s`$ 、元のトランザクション起点者[^10] $`o`$ 、利用可能 gas $`g`$ 、実効 gas 価格 $`p`$ 、付与額 $`v`$ 、任意長バイト配列である初期化 EVM コード $`\mathbf{i}`$ 、現在のメッセージ呼び出し／コントラクト作成スタック深度 $`e`$ 、新しいアカウント・アドレスの salt $`\zeta`$ 、最後に状態変更の許可 $`w`$ である。salt $`\zeta`$ は存在しない場合がある（ $`\zeta = \varnothing`$ ）。形式的には

<span id="eq-92"></span>

```math
\zeta \in \mathbb{B}_{32} \cup \mathbb{B}_{0} \qquad \text{(92)}
```

である。[CREATE2](#create2) による作成なら $`\zeta \neq \varnothing`$ となる。

作成関数 $`\Lambda`$ を形式的に定義する。この関数は、これらの値に状態 $`\boldsymbol{\sigma}`$ と累積サブ状態 $`A`$ を合わせて評価し、新しい状態、残存gas、新しい累積サブ状態、ステータス・コード、出力からなるタプル $`(\boldsymbol{\sigma}', g', A', z, \mathbf{o})`$ を返す。

<span id="eq-93"></span>

```math
(\boldsymbol{\sigma}', g', A', z, \mathbf{o}) \equiv \Lambda(\boldsymbol{\sigma}, A, s, o, g, p, v, \mathbf{i}, e, \zeta, w) \qquad \text{(93)}
```

新しいアカウントのアドレスは、送信者と[アカウントnonce](#account_nonce)だけを含む構造を[RLP](#rlp)符号化し、そのKeccak-256ハッシュの右端160ビットを取ったものとして定義される。[CREATE2](#create2)では規則が異なり、[(Buterin 2018)](#ref-EIP-1014)によるEIP-1014に記述されている。二つの場合を合わせ、新しいアカウントの結果アドレス $`a`$ を次のように定義する。

<span id="eq-94"></span><span id="eq-95"></span><span id="eq-96"></span><span id="eq:new-address"></span>

```math
\begin{aligned}
a & \equiv \mathtt{ADDR}(s, \boldsymbol{\sigma}[s]_{\mathrm{n}} - 1, \zeta, \mathbf{i}) & \qquad \text{(94)} \\
\mathtt{ADDR}(s, n, \zeta, \mathbf{i}) & \equiv \mathcal{B}_{96..255}\Big(\mathtt{KEC}\big( L_{\mathrm{A}}(s, n, \zeta, \mathbf{i})\big) \Big) & \qquad \text{(95)} \\
L_{\mathrm{A}}(s, n, \zeta, \mathbf{i}) & \equiv \begin{cases}
\mathtt{RLP}\big(\;(s, n)\;\big) & \text{if}\ \zeta = \varnothing \\
(255) \cdot s \cdot \zeta \cdot \mathtt{KEC}(\mathbf{i}) & \text{otherwise}
\end{cases} & \qquad \text{(96)}
\end{aligned}
```

ここで $`\cdot`$ はバイト配列の連結であり、 $`\mathcal{B}_{a..b}(X)`$ はバイナリ・データ $`X`$ の添字範囲 $`[a, b]`$ のビットを含むバイナリ値へ評価される。また $`\boldsymbol{\sigma}[x]`$ は $`x`$ のアドレス状態であり、存在しなければ $`\varnothing`$ である。送信者のnonce値より1小さい値を用いることに注意されたい。この呼出しに先立って送信者アカウントのnonceを増加させたと仮定しているため、用いる値は、その原因となったトランザクションまたはVM演算の開始時点における送信者のnonceである。

新しいアカウントのアドレスをアクセス済みアカウント集合へ追加する。

<span id="eq-97"></span>

```math
A^{*} \equiv A \quad \text{except} \quad A^{*}_{\mathbf{a}} \equiv A_{\mathbf{a}} \cup \{a\} \qquad \text{(97)}
```

アカウントのnonceは初期値1、残高は渡された値、ストレージは空、コード・ハッシュは空文字列のKeccak 256ビット・ハッシュとして定義される。また送信者の残高から渡された値を減じる。したがって変更後の状態は $`\boldsymbol{\sigma}^{*}`$ となる。

<span id="eq-98"></span>

```math
\boldsymbol{\sigma}^{*} \equiv \boldsymbol{\sigma} \quad \text{except:} \qquad \text{(98)}
```

<span id="eq-99"></span><span id="eq-100"></span><span id="eq-101"></span>

```math
\begin{aligned}
\boldsymbol{\sigma}^{*}[a] &=& \big( 1, v + v', \mathtt{TRIE}(\varnothing), \mathtt{KEC}\big(()\big) \big) & \qquad \text{(99)} \\
\boldsymbol{\sigma}^{*}[s] &=& \begin{cases}
\varnothing & \text{if}\ \boldsymbol{\sigma}[s] = \varnothing \ \wedge\ v = 0 \\
\mathbf{a}^{*} & \text{otherwise}
\end{cases} & \qquad \text{(100)} \\
\mathbf{a}^{*} &\equiv& (\boldsymbol{\sigma}[s]_{\mathrm{n}}, \boldsymbol{\sigma}[s]_{\mathrm{b}} - v, \boldsymbol{\sigma}[s]_{\mathbf{s}}, \boldsymbol{\sigma}[s]_{\mathrm{c}}) & \qquad \text{(101)}
\end{aligned}
```

ここで、アカウントが以前から存在していた場合、 $`v'`$ はその既存の残高である。

<span id="eq-102"></span>

```math
v' \equiv \begin{cases}
0 & \text{if} \quad \boldsymbol{\sigma}[a] = \varnothing\\
\boldsymbol{\sigma}[a]_{\mathrm{b}} & \text{otherwise}
\end{cases} \qquad \text{(102)}
```

最後に、実行モデル（[第9節](#ch:model)参照）に従って初期化 EVM コード $`\mathbf{i}`$ を実行し、アカウントを初期化する。コード実行は、実行状態の内部に限られない複数の事象を生じ得る。アカウントのストレージを変更し、別のアカウントを作成し、別のメッセージ呼び出しを行える。したがってコード実行関数 $`\Xi`$ の値は、結果状態 $`\boldsymbol{\sigma}^{**}`$ 、残りの利用可能 gas $`g^{**}`$ 、結果として得られる累積サブ状態 $`A^{**}`$ 、アカウントの本体コード $`\mathbf{o}`$ のタプルである。

<span id="eq-103"></span>

```math
(\boldsymbol{\sigma}^{**}, g^{**}, A^{**}, \mathbf{o}) \equiv \Xi(\boldsymbol{\sigma}^{*}, g, A^{*}, I) \qquad \text{(103)}
```

ここで $`I`$ は[実行環境](#exec_env)のパラメータを含む。すなわち、

<span id="eq-104"></span><span id="eq-105"></span><span id="eq-106"></span><span id="eq-107"></span><span id="eq-108"></span><span id="eq-109"></span><span id="eq-110"></span><span id="eq-111"></span><span id="eq-112"></span>

```math
\begin{aligned}
I_{\mathrm{a}} & \equiv & a & \qquad \text{(104)} \\
I_{\mathrm{o}} & \equiv & o & \qquad \text{(105)} \\
I_{\mathrm{p}} & \equiv & p & \qquad \text{(106)} \\
I_{\mathbf{d}} & \equiv & () & \qquad \text{(107)} \\
I_{\mathrm{s}} & \equiv & s & \qquad \text{(108)} \\
I_{\mathrm{v}} & \equiv & v & \qquad \text{(109)} \\
I_{\mathbf{b}} & \equiv & \mathbf{i} & \qquad \text{(110)} \\
I_{\mathrm{e}} & \equiv & e & \qquad \text{(111)} \\
I_{\mathrm{w}} & \equiv & w & \qquad \text{(112)}
\end{aligned}
```

この呼出しには入力データがないため、 $`I_{\mathbf{d}}`$ は空タプルへ評価される。 $`I_{\mathrm{H}}`$ に特別な扱いはなく、ブロックチェーンから決定される。

コード実行は gas を消費し、gas はゼロ未満になれないため、コードが自然な停止状態へ達する前に実行が終了することがある。この場合（およびほかのいくつかの例外的場合）、gas 不足（OOG）例外が発生したという。評価結果の状態は空集合 $`\varnothing`$ と定義し、作成操作全体は状態へ影響せず、実質的に作成を試みる直前の状態を残す。

初期化コードが正常に完了した場合、作成されたコントラクトのコード・サイズに比例する最終的なコントラクト作成コスト、すなわちコード格納コスト $`c`$ が支払われる。

<span id="eq-113"></span>

```math
c \equiv G_{\mathrm{codedeposit}} \times \lVert \mathbf{o} \rVert \qquad \text{(113)}
```

これを支払うだけの gas が残っていない、すなわち $`g^{**} < c`$ の場合も gas 不足例外を宣言する。

このような例外条件では残り gas はゼロとなる。すなわち、トランザクションの受信によりコントラクト作成が行われた場合でも、コントラクト作成の固有コストの支払いには影響せず、いずれにせよ支払われる。ただし gas 不足時にはトランザクションの値を作成が中断されたコントラクトのアドレスへ移転せず、コントラクトのコードも格納しない。

このような例外が発生しなければ、残り gas を起点者へ払い戻し、変更後の状態を永続化できる。したがって、結果状態、gas、累積サブ状態、ステータス・コードを形式的に $`(\boldsymbol{\sigma}', g', A', z)`$ と規定する。

<span id="eq-114"></span><span id="eq-115"></span><span id="eq-116"></span><span id="eq-117"></span><span id="eq-118"></span>

```math
\begin{aligned}
\quad g' \equiv & \begin{cases}
0 & \text{if} \quad F \\
g^{**} - c & \text{otherwise} \\
\end{cases} & \qquad \text{(114)} \\
\quad \boldsymbol{\sigma}' \equiv & \begin{cases}
\boldsymbol{\sigma} & \text{if} \quad F \ \lor\ \boldsymbol{\sigma}^{**} = \varnothing \\
\boldsymbol{\sigma}^{**} \quad \text{except:} & \\
\quad\boldsymbol{\sigma}'[a] = \varnothing & \text{if} \quad \mathtt{DEAD}(\boldsymbol{\sigma}^{**}, a) \\
\boldsymbol{\sigma}^{**} \quad \text{except:} & \\
\quad\boldsymbol{\sigma}'[a]_{\mathrm{c}} = \texttt{KEC}(\mathbf{o}) & \text{otherwise}
\end{cases} & \qquad \text{(115)} \\
\quad A' \equiv & \begin{cases}
A^{*} & \text{if} \quad F \ \lor\ \boldsymbol{\sigma}^{**} = \varnothing \\
A^{**} & \text{otherwise} \\
\end{cases} & \qquad \text{(116)} \\
\quad z \equiv & \begin{cases}
0 & \text{if} \quad F \ \lor\ \boldsymbol{\sigma}^{**} = \varnothing \\
1 & \text{otherwise}
\end{cases} & \qquad \text{(117)} \\
\text{where} \\
F \equiv  & \big( \boldsymbol{\sigma}[a] \neq \varnothing \ \wedge\ \big(\boldsymbol{\sigma}[a]_c \neq \texttt{KEC}\big(()\big) \vee \boldsymbol{\sigma}[a]_n \neq 0 \big) \big) \quad \vee & \qquad \text{(118)} \\
&(\boldsymbol{\sigma}^{**} = \varnothing \ \wedge\ \mathbf{o} = \varnothing) \quad \vee \\
&g^{**} < c \quad \vee \\
&\lVert \mathbf{o} \rVert > 24576 \quad \vee \\
&\mathbf{o}[0] = \texttt{0xef}
\end{aligned}
```

<span id="contract_creation_result"></span>

$`F`$ の最後の条件は、コントラクト・コードがバイト `0xef` で始まってはならないことを示す点に注意されたい（[(Beregszaszi et al. 2021)](#ref-EIP-3541)によるEIP-3541を参照）。

$`\boldsymbol{\sigma}'`$ の決定における但し書きは、初期化コード実行の結果バイト列 $`\mathbf{o}`$ が、新たに作成されたアカウントの最終的な本体コードを指定することを定める。

意図する結果は、付与額を伴う新しいコントラクトの作成成功か、値の移転を伴わない新規コントラクトの不作成のいずれかである。さらに、初期化コードの実行が[リバート](#REVERT)した場合（ $`\boldsymbol{\sigma}^{**} = \varnothing \ \wedge\ \mathbf{o} \neq \varnothing`$ ）、ほかの例外がなければ結果 gas $`g'`$ は枯渇しないが、新しいアカウントは作成されない。

## 7.1. 微妙な点

初期化コードの実行中、新たに作成されたアドレスは存在するが、固有の本体コードを持たない[^11]。したがって、この間に受け取るメッセージ呼び出しではコードを実行しない。初期化実行が SELFDESTRUCT 命令で終わる場合、トランザクション完了前にアカウントが削除されるため問題にならない。通常の STOP コードの場合、または返されたコードが空の場合、状態にはゾンビ・アカウントが残り、残高は永久にそのアカウントへロックされる。

<span id="ch:call"></span>

# 8. メッセージ呼び出し

メッセージ呼び出しの実行には、送信者 $`s`$ 、トランザクション起点者 $`o`$ 、受信者 $`r`$ 、コードを実行するアカウント $`c`$ （通常は受信者と同じ）、利用可能 gas $`g`$ 、値 $`v`$ 、実効 gas 価格 $`p`$ 、呼び出しの入力データである任意長バイト配列 $`\mathbf{d}`$ 、現在のメッセージ呼び出し／コントラクト作成スタック深度 $`e`$ 、最後に状態変更の許可 $`w`$ が必要である。

メッセージ呼び出しには、新しい状態と累積トランザクション・サブ状態への評価に加えて、バイト配列 $`\mathbf{o}`$ で表す出力データという追加の構成要素がある。これはトランザクション実行時には無視されるが、メッセージ呼び出しはVMコードの実行によって開始される場合があり、その場合にはこの情報を用いる。

<span id="eq-119"></span>

```math
(\boldsymbol{\sigma}', g', A', z, \mathbf{o}) \equiv {\Theta}(\boldsymbol{\sigma}, A, s, o, r, c, g, p, v, \tilde{v}, \mathbf{d}, e, w) \qquad \text{(119)}
```

DELEGATECALL命令では、移転する値 $`v`$ と、実行文脈から見える値 $`\tilde{v}`$ とを区別する必要があることに注意されたい。

最初の遷移状態 $`\boldsymbol{\sigma}_1`$ を、送信者から受信者へ値を移転した元の状態として定義する。

<span id="eq-120"></span>

```math
\boldsymbol{\sigma}_1[r]_{\mathrm{b}} \equiv \boldsymbol{\sigma}[r]_{\mathrm{b}} + v \quad\wedge\quad \boldsymbol{\sigma}_1[s]_{\mathrm{b}} \equiv \boldsymbol{\sigma}[s]_{\mathrm{b}} - v \qquad \text{(120)}
```

ただし $`s = r`$ の場合を除く。

本稿全体を通じて、 $`\boldsymbol{\sigma}_1[r]`$ が元々未定義であった場合、コードも状態もなく、残高とnonceがゼロのアカウントとして作成されると仮定する。したがって、直前の式は次の意味に解するべきである。

<span id="eq-121"></span>

```math
\boldsymbol{\sigma}_1 \equiv \boldsymbol{\sigma}_1' \quad \text{except:} \qquad \text{(121)}
```

<span id="eq-122"></span>

```math
\boldsymbol{\sigma}_1[s] \equiv \begin{cases}
\varnothing & \text{if}\ \boldsymbol{\sigma}_1'[s] = \varnothing \ \wedge\ v = 0 \\
\mathbf{a}_1 &\text{otherwise}
\end{cases} \qquad \text{(122)}
```

<span id="eq-123"></span>

```math
\mathbf{a}_1 \equiv \left(\boldsymbol{\sigma}_1'[s]_{\mathrm{n}}, \boldsymbol{\sigma}_1'[s]_{\mathrm{b}} - v, \boldsymbol{\sigma}_1'[s]_{\mathbf{s}}, \boldsymbol{\sigma}_1'[s]_{\mathrm{c}}\right) \qquad \text{(123)}
```

<span id="eq-124"></span>

```math
\text{and}\quad \boldsymbol{\sigma}_1' \equiv \boldsymbol{\sigma} \quad \text{except:} \qquad \text{(124)}
```

<span id="eq-125"></span>

```math
\begin{cases}
\boldsymbol{\sigma}_1'[r] \equiv (0, v, \mathtt{TRIE}(\varnothing), \mathtt{KEC}(())) & \text{if} \quad \boldsymbol{\sigma}[r] = \varnothing \wedge v \neq 0 \\
\boldsymbol{\sigma}_1'[r] \equiv \varnothing & \text{if}\quad \boldsymbol{\sigma}[r] = \varnothing \wedge v = 0 \\
\boldsymbol{\sigma}_1'[r] \equiv \mathbf{a}_1' & \text{otherwise}
\end{cases} \qquad \text{(125)}
```

<span id="eq-126"></span>

```math
\mathbf{a}_1' \equiv (\boldsymbol{\sigma}[r]_{\mathrm{n}}, \boldsymbol{\sigma}[r]_{\mathrm{b}} + v, \boldsymbol{\sigma}[r]_{\mathbf{s}}, \boldsymbol{\sigma}[r]_{\mathrm{c}}) \qquad \text{(126)}
```

アカウントの関連コード（Keccak-256 ハッシュが $`\boldsymbol{\sigma}[c]_{\mathrm{c}}`$ となる断片）は、実行モデル（[第9節](#ch:model)参照）に従って実行する。コントラクト作成と同様、実行が例外的に停止した場合（gas の枯渇、スタック・アンダーフロー、無効なジャンプ先、無効な命令など）、呼び出し元に gas を払い戻さず、状態を残高移転直前、すなわち $`\boldsymbol{\sigma}`$ へ戻す。

<span id="eq-127"></span><span id="eq-128"></span><span id="eq-129"></span><span id="eq-130"></span><span id="eq-131"></span><span id="eq-132"></span><span id="eq-133"></span><span id="eq-134"></span><span id="eq-135"></span><span id="eq-136"></span><span id="eq-137"></span><span id="eq-138"></span><span id="eq-139"></span><span id="code_execution_result"></span>

```math
\begin{aligned}
\boldsymbol{\sigma}' & \equiv & \begin{cases}
\boldsymbol{\sigma} & \text{if} \quad \boldsymbol{\sigma}^{**} = \varnothing \\
\boldsymbol{\sigma}^{**} & \text{otherwise}
\end{cases} & \qquad \text{(127)} \\
g' & \equiv & \begin{cases}
0 & \text{if} \quad \boldsymbol{\sigma}^{**} = \varnothing \ \wedge \\
&\quad \mathbf{o} = \varnothing \\
g^{**} & \text{otherwise}
\end{cases} & \qquad \text{(128)} \\
A' & \equiv & \begin{cases}
A & \text{if} \quad \boldsymbol{\sigma}^{**} = \varnothing \\
A^{**} & \text{otherwise}
\end{cases} & \qquad \text{(129)} \\
z & \equiv & \begin{cases}
0 & \text{if} \quad \boldsymbol{\sigma}^{**} = \varnothing \\
1 & \text{otherwise}
\end{cases} & \qquad \text{(130)} \\
(\boldsymbol{\sigma}^{**}, g^{**}, A^{**}, \mathbf{o}) & \equiv & \Xi & \qquad \text{(131)} \\
I_{\mathrm{a}} & \equiv & r & \qquad \text{(132)} \\
I_{\mathrm{o}} & \equiv & o & \qquad \text{(133)} \\
I_{\mathrm{p}} & \equiv & p & \qquad \text{(134)} \\
I_{\mathbf{d}} & \equiv & \mathbf{d} & \qquad \text{(135)} \\
I_{\mathrm{s}} & \equiv & s & \qquad \text{(136)} \\
I_{\mathrm{v}} & \equiv & \tilde{v} & \qquad \text{(137)} \\
I_{\mathrm{e}} & \equiv & e & \qquad \text{(138)} \\
I_{\mathrm{w}} & \equiv & w & \qquad \text{(139)}
\end{aligned}
```

ここで、

<span id="eq-140"></span>

```math
\Xi \equiv \begin{cases}
\Xi_{\mathtt{ECREC}}    (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 1 \\
\Xi_{\mathtt{SHA256}}   (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 2 \\
\Xi_{\mathtt{RIP160}}   (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 3 \\
\Xi_{\mathtt{ID}}       (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 4 \\
\Xi_{\mathtt{EXPMOD}}   (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 5 \\
\Xi_{\mathtt{BN\_ADD}}  (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 6 \\
\Xi_{\mathtt{BN\_MUL}}  (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 7 \\
\Xi_{\mathtt{SNARKV}}   (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 8 \\
\Xi_{\mathtt{BLAKE2\_F}}(\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 9 \\
\Xi                     (\boldsymbol{\sigma}_1, g, A, I) & \text{otherwise} \end{cases} \qquad \text{(140)}
```

かつ

<span id="eq-141"></span>

```math
\mathtt{KEC}(I_{\mathbf{b}}) = \boldsymbol{\sigma}[c]_{\mathrm{c}} \qquad \text{(141)}
```

とする。 $`I_{\mathbf{b}}`$ を決定可能にするため、クライアントはそれ以前のある時点でペア $`(\mathtt{KEC}(I_{\mathbf{b}}), I_{\mathbf{b}})`$ を格納済みであると仮定する。

見て分かるように、メッセージ呼び出しを評価する際の一般実行フレームワーク $`\Xi`$ の使用には九つの例外がある。これらはいわゆる「プリコンパイル済み」コントラクトであり、後に*ネイティブ拡張*となり得る予備的なアーキテクチャとして意図されている。アドレス1から9のコントラクトは、それぞれ楕円曲線公開鍵復元関数、SHA2 256ビット・ハッシュ方式、RIPEMD 160ビット・ハッシュ方式、恒等関数、任意精度モジュラー累乗、楕円曲線加算、楕円曲線スカラー乗算、楕円曲線ペアリング検査、BLAKE2圧縮関数 $`\mathtt{F}`$ を実行する。完全な形式的定義は[付録E](#app:precompiled)にある。<span id="precompiled_set"></span>プリコンパイル済みコントラクトのアドレス集合を $`\pi`$ と表す。

<span id="eq-142"></span>

```math
\pi \equiv \{1, 2, 3, 4, 5, 6, 7, 8, 9 \} \qquad \text{(142)}
```

<span id="ch:model"></span>

# 9. 実行モデル

実行モデルは、バイトコード命令列と環境データの小さなタプルが与えられたとき、システム状態をどのように変更するかを規定する。これは Ethereum 仮想マシン（EVM）として知られる仮想状態機械の形式モデルによって規定される。EVM は*準*チューリング完全な機械である。「準」という限定は、実行できる計算の総量を制限する *gas* というパラメータにより、計算が本質的に有界であることに由来する。

## 9.1. 基礎

EVM は単純なスタック・ベースのアーキテクチャである。マシンのワード・サイズ（したがってスタック項目のサイズ）は256ビットである。これは Keccak-256 ハッシュ方式と楕円曲線計算を容易にするために選ばれた。メモリ・モデルは単純なワード・アドレス指定バイト配列である。スタックの最大サイズは $`1024`$ である。マシンには独立したストレージ・モデルもある。概念上はメモリに似るが、バイト配列ではなくワード・アドレス指定可能なワード配列である。揮発性のメモリと異なり、ストレージは不揮発性で、システム状態の一部として維持される。ストレージとメモリのすべての位置は、初期状態でゼロと明確に定義される。

<span id="tnref-4"></span>[訳注4](#tn-4)

マシンは標準的なフォン・ノイマン・アーキテクチャには従わない。プログラム・コードを一般にアクセス可能なメモリまたはストレージへ格納せず、特殊命令を介してのみ相互作用できる仮想 ROM に別途格納する。

マシンは、スタック・アンダーフローや無効な命令など、いくつかの理由で例外実行となり得る。gas 不足例外と同様、状態変更は維持されない。マシンは直ちに停止し、問題を実行主体（トランザクション処理器、または再帰的には実行を生成した環境）へ報告し、実行主体が別途処理する。

## 9.2. 手数料の概要

gas建ての手数料は三つの異なる状況で課され、いずれも演算実行の前提条件となる。第一かつ最も一般的なのは、演算の計算に固有の手数料である（[付録G](#app:fees)参照）。第二に、下位のメッセージ呼び出しまたはコントラクト作成への支払いを構成するためgasが差し引かれることがある。これはCREATE、CREATE2、CALL、CALLCODEへの支払いの一部となる。最後に、メモリ使用量の増加によりgasが支払われることがある。

アカウントの実行全体にわたり、支払うべきメモリ使用手数料の総額は、読み書きを問わずすべてのメモリ・インデックスを範囲内に含めるために必要な32バイトの最小倍数に比例する。これは必要時に支払われるため、以前に索引付けしたいかなるメモリよりも少なくとも32バイト先の領域を参照すれば、必ず追加のメモリ使用手数料が生じる。この手数料により、アドレスが32ビットの境界を超える可能性は極めて低い。それでも実装はこの事態を処理できなければならない。

ストレージ手数料の挙動はやや複雑である。ストレージ使用量（全ノード上の状態データベースの増大に直結する）の最小化を促すため、ストレージ項目を消去する演算では実行手数料が免除されるだけでなく、条件付きの還付が与えられる。実際には、ストレージ位置を最初に使用するコストが通常使用より大幅に高いため、この還付は事実上前払いされている。

EVMのgasコストの厳密な定義は[付録H](#app:vm)を参照されたい。

<span id="exec_env"></span>

## 9.3. 実行環境

実行環境では、システム状態 $`\boldsymbol{\sigma}`$ 、計算に残されたgas $`g`$ 、累積サブ状態 $`A`$ に加えて、実行主体が提供しなければならない重要な情報がいくつか用いられる。これらはタプル $`I`$ に含まれる。

- $`I_{\mathrm{a}}`$ ：実行中のコードを所有するアカウントのアドレス。

- $`I_{\mathrm{o}}`$ ：この実行の起点となったトランザクションの送信者アドレス。

- $`I_{\mathrm{p}}`$ ：この実行の起点となったトランザクションの署名者が支払うgas価格。[第6節](#ch:transactions)の実効gas価格 [$`p`$](#effective_gas_price_p) として定義される。

- $`I_{\mathbf{d}}`$ ：この実行への入力データであるバイト配列。実行主体がトランザクションなら、トランザクション・データとなる。

- $`I_{\mathrm{s}}`$ ：コードを実行させたアカウントのアドレス。実行主体がトランザクションなら、トランザクション送信者となる。

- $`I_{\mathrm{v}}`$ ：実行と同じ手続きの一部としてこのアカウントへ渡されるWei単位の値。実行主体がトランザクションなら、トランザクション値となる。

- $`I_{\mathbf{b}}`$ ：実行するマシン・コードのバイト配列。

- $`I_{\mathrm{H}}`$ ：現在のブロックのブロック・ヘッダ。

- $`I_{\mathrm{e}}`$ ：現在のメッセージ呼び出しまたはコントラクト作成の深さ（現在実行中のCALLまたはCREATE(2)の数）。

- $`I_{\mathrm{w}}`$ ：状態変更の許可。

実行モデルは関数 $`\Xi`$ を定義する。この関数は、これらの定義が与えられたとき、結果状態 $`\boldsymbol{\sigma}'`$ 、残存gas $`g'`$ 、結果の累積サブ状態 $`A'`$ 、結果出力 $`\mathbf{o}`$ を計算できる。ここでは次のように定義する。

<span id="eq-143"></span>

```math
(\boldsymbol{\sigma}', g', A', \mathbf{o}) \equiv \Xi(\boldsymbol{\sigma}, g, A, I) \qquad \text{(143)}
```

なお、累積サブ状態 $`A`$ は[第6.1節](#ch:substate)で定義したものである。

## 9.4. 実行の概要

ここで $`\Xi`$ 関数を定義しなければならない。実用的な実装の多くでは、完全なシステム状態 $`\boldsymbol{\sigma}`$ とマシン状態 $`\boldsymbol{\mu}`$ の対を反復的に進行させるものとしてモデル化される。形式的には、関数 $`X`$ を用いて再帰的に定義する。これは、状態機械の1サイクルの結果を定義する反復関数 $`O`$ と、現在状態がマシンの[例外停止](#zhalt)状態かどうかを判定する関数 [$`Z`$](#zhalt)、および現在状態がマシンの[正常停止](#hhalt)状態である場合、かつその場合に限り命令の出力データを指定する関数 [$`H`$](#hhalt) を用いる。

<div id="empty_sequence_vs_empty_set">

</div>

$`()`$ と表す空列は、 $`\varnothing`$ と表す空集合とは等しくない。これは $`H`$ の出力を解釈する際に重要である。実行を継続すべきとき $`H`$ は $`\varnothing`$ と評価され、停止すべきときは（空である可能性もある）列と評価される。

<span id="eq-144"></span><span id="eq-145"></span><span id="eq-146"></span><span id="eq-147"></span><span id="eq-148"></span><span id="eq-149"></span><span id="eq-150"></span><span id="eq-151"></span>

```math
\begin{aligned}
\Xi(\boldsymbol{\sigma}, g, A, I) & \equiv & (\boldsymbol{\sigma}'\!, \boldsymbol{\mu}'_{\mathrm{g}}, A', \mathbf{o}) & \qquad \text{(144)} \\
(\boldsymbol{\sigma}', \boldsymbol{\mu}'\!, A', ..., \mathbf{o}) & \equiv & X\big((\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I)\big) & \qquad \text{(145)} \\
\boldsymbol{\mu}_{\mathrm{g}} & \equiv & g & \qquad \text{(146)} \\
\boldsymbol{\mu}_{\mathrm{pc}} & \equiv & 0 & \qquad \text{(147)} \\
\boldsymbol{\mu}_{\mathbf{m}} & \equiv & (0, 0, ...) & \qquad \text{(148)} \\
\boldsymbol{\mu}_{\mathrm{i}} & \equiv & 0 & \qquad \text{(149)} \\
\boldsymbol{\mu}_{\mathbf{s}} & \equiv & () & \qquad \text{(150)} \\
\boldsymbol{\mu}_{\mathbf{o}} & \equiv & () & \qquad \text{(151)}
\end{aligned}
```

<span id="eq-152"></span><span id="eq:X-def"></span>

```math
X\big( (\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \big) \equiv \begin{cases}
\big(\varnothing, \boldsymbol{\mu}, A, I, \varnothing\big) & \text{if} \quad Z(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \\
\big(\varnothing, \boldsymbol{\mu}', A, I, \mathbf{o}\big) & \text{if} \quad w = \text{REVERT} \\
O(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \cdot \mathbf{o} & \text{if} \quad \mathbf{o} \neq \varnothing \\
X\big(O(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I)\big) & \text{otherwise} \\
\end{cases} \qquad \text{(152)}
```

ここで、

<span id="eq-153"></span><span id="eq-154"></span><span id="eq-155"></span><span id="eq-156"></span>

```math
\begin{aligned}
\mathbf{o} & \equiv & H(\boldsymbol{\mu}, I) & \qquad \text{(153)} \\
(a, b, c, d) \cdot e & \equiv & (a, b, c, d, e) & \qquad \text{(154)} \\
\boldsymbol{\mu}' & \equiv & \boldsymbol{\mu}\ \text{except:} & \qquad \text{(155)} \\
\boldsymbol{\mu}'_{\mathrm{g}} & \equiv & \boldsymbol{\mu}_{\mathrm{g}} - C(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) & \qquad \text{(156)}
\end{aligned}
```

$`\Xi`$ を評価するときは、第4要素 $`I'`$ を捨て、結果のマシン状態 $`\boldsymbol{\mu}'`$ から残存gas $`\boldsymbol{\mu}'_{\mathrm{g}}`$ を取り出す点に注意されたい。

このように、[$`Z`$](#zhalt) が真となって現在状態が例外的であり、マシンを停止してすべての変更を破棄すべきことを示すか、[$`H`$](#hhalt) が空集合ではなく列となってマシンが制御された停止に達したことを示すまで、 $`X`$ を循環させる（ここでは再帰的だが、実装では通常、単純な反復ループを用いることが期待される）。

### 9.4.1. マシン状態

マシン状態 $`\boldsymbol{\mu}`$ はタプル $`(g, pc, \mathbf{m}, i, \mathbf{s}, \mathbf{o})`$ として定義される。各要素は、利用可能なgas、プログラム・カウンタ $`pc \in \mathbb{N}_{256}`$ 、メモリ内容、メモリ内の有効ワード数（位置0から連続して数える）、スタック内容、リターン・データ・バッファである。メモリ内容 $`\boldsymbol{\mu}_{\mathbf{m}}`$ は、大きさ $`2^{256}`$ のゼロ列である。

読みやすさのため、スモールキャップで記した命令ニーモニック（例：ADD）は、その数値表現として解釈されたい。命令の完全な表と詳細は[付録H](#app:vm)に示す。

$`Z`$ 、 $`H`$ 、 $`O`$ を定義するため、 $`w`$ を現在実行される演算として定義する。

<span id="eq-157"></span><span id="eq:currentoperation"></span>

```math
w \equiv \begin{cases} I_{\mathbf{b}}[\boldsymbol{\mu}_{\mathrm{pc}}] & \text{if} \quad \boldsymbol{\mu}_{\mathrm{pc}} < \lVert I_{\mathbf{b}} \rVert \\
\text{STOP} & \text{otherwise}
\end{cases} \qquad \text{(157)}
```

さらに、削除および追加されるスタック項目数を指定する固定量 $`\mathbf{\delta}`$ と $`\mathbf{\alpha}`$ を仮定する。いずれも命令によって添字付けでき、命令コスト関数 $`C`$ は与えられた命令を実行する完全なコストをgas単位で評価する。

<span id="zhalt"></span>

### 9.4.2. 例外停止

<div id="Exceptional_Halting_function_Z">

</div>

例外停止関数 $`Z`$ を次のように定義する。

<span id="eq-158"></span>

```math
Z(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \equiv
\begin{array}{l}
\boldsymbol{\mu}_g < C(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \quad \vee \\
\mathbf{\delta}_w = \varnothing \quad \vee \\
\lVert\boldsymbol{\mu}_\mathbf{s}\rVert < \mathbf{\delta}_w \quad \vee \\
( w = \text{JUMP} \; \wedge \; \boldsymbol{\mu}_\mathbf{s}[0] \notin D(I_\mathbf{b}) ) \quad \vee \\
( w = \text{JUMPI} \; \wedge \; \boldsymbol{\mu}_\mathbf{s}[1] \neq 0 \; \wedge \\
\quad \boldsymbol{\mu}_\mathbf{s}[0] \notin D(I_\mathbf{b}) ) \quad \vee \\
( w = \text{RETURNDATACOPY} \; \wedge \\ \quad \boldsymbol{\mu}_{\mathbf{s}}[1] + \boldsymbol{\mu}_{\mathbf{s}}[2] > \lVert\boldsymbol{\mu}_{\mathbf{o}}\rVert) \quad \vee \\
\lVert\boldsymbol{\mu}_\mathbf{s}\rVert - \mathbf{\delta}_w + \mathbf{\alpha}_w > 1024 \quad \vee \\
( \neg I_{\mathrm{w}} \; \wedge \; W(w, \boldsymbol{\mu}) ) \quad \vee \\
( w = \text{SSTORE} \; \wedge \; \boldsymbol{\mu}_g \leqslant G_{\mathrm{callstipend}} )
\end{array} \qquad \text{(158)}
```

ここで、

<span id="eq-159"></span>

```math
W(w, \boldsymbol{\mu}) \equiv
\begin{array}{l}
w \in \{\text{CREATE}, \text{CREATE2}, \text{SSTORE},\\ \text{SELFDESTRUCT}\} \ \vee \\
\text{LOG0} \le w \; \wedge \; w \le \text{LOG4} \quad \vee \\
w = \text{CALL} \; \wedge \; \boldsymbol{\mu}_{\mathbf{s}}[2] \neq 0
\end{array} \qquad \text{(159)}
```

これは、gasが不足する場合、命令が無効である（したがってその $`\delta`$ 添字が未定義である）場合、スタック項目が不足する場合、JUMP/JUMPIの宛先が無効である場合、新しいスタック・サイズが1024を超える場合、または静的呼び出し中に状態変更を試みる場合に、実行が例外停止状態となることを述べている。注意深い読者は、これが、いかなる命令もその実行途中で例外停止を引き起こすことはない、ということを含意すると分かるだろう。また、[SSTORE](#SSTORE)命令を実行する直前の残存gasが呼び出し給付量 $`G_{\mathrm{callstipend}}`$ 以下である場合も実行は例外停止状態となる。詳細は[(Tang 2019)](#ref-EIP-2200)によるEIP-2200を参照されたい。

### 9.4.3. ジャンプ先の妥当性

先に、実行中のコードが与えられたとき妥当なジャンプ先の集合を決定する関数として $`D`$ を用いた。これを、コード内でJUMPDEST命令が占めるすべての位置として定義する。

そのような位置はすべて、PUSH演算のデータ部分ではなく妥当な命令境界上になければならず、コード末尾に暗黙に定義される[STOP](#stop)演算ではなく、コードの明示的に定義された部分内に現れなければならない。

形式的には、

<span id="eq-160"></span>

```math
D(\mathbf{c}) \equiv D_{\mathrm{J}}(\mathbf{c}, 0) \qquad \text{(160)}
```

ここで、

<span id="eq-161"></span>

```math
D_{\mathrm{J}}(\mathbf{c}, i) \equiv \begin{cases}
\{\} & \text{if} \quad i \geqslant \lVert \mathbf{c} \rVert  \\
\{ i \} \cup D_{\mathrm{J}}(\mathbf{c}, N(i, \mathbf{c}[i])) & \\
\quad\quad\text{if} \quad \mathbf{c}[i] = \text{JUMPDEST} \\
D_{\mathrm{J}}(\mathbf{c}, N(i, \mathbf{c}[i])) & \text{otherwise} \\
\end{cases} \qquad \text{(161)}
```

ここで $`N`$ は、PUSH命令のデータがあればそれを飛ばした、コード内の次の妥当な命令位置である。

<span id="eq-162"></span>

```math
N(i, w) \equiv \begin{cases}
i + w - \text{PUSH1} + 2 & \\
\quad\quad\text{if} \quad w \in [\text{PUSH1}, \text{PUSH32}] \\
i + 1 & \text{otherwise} \end{cases} \qquad \text{(162)}
```

<span id="hhalt"></span>

### 9.4.4. 正常停止

<div id="normal_halting_function_H">

</div>

正常停止関数 $`H`$ を次のように定義する。

<span id="eq-163"></span>

```math
H(\boldsymbol{\mu}, I) \equiv \begin{cases}
H_{\text{RETURN}}(\boldsymbol{\mu}) \ \text{if} \quad w \in \{\text{RETURN}, \text{REVERT}\} &\\
() \quad\quad\ \text{if} \quad w \in \{ \text{STOP}, \text{SELFDESTRUCT} \} &\\
\varnothing \quad\quad\ \text{otherwise}&
\end{cases} \qquad \text{(163)}
```

データを返す停止演算 [RETURN](#RETURN) と [REVERT](#REVERT) には、特別な関数 $`H_{\text{RETURN}}`$ がある。[ここ](#empty_sequence_vs_empty_set)で論じた空列と空集合の違いにも注意されたい。

## 9.5. 実行サイクル

スタック項目は列の左端、すなわち低いインデックス側で追加または削除される。ほかのすべての項目は変化しない。

<span id="eq-164"></span><span id="eq-165"></span><span id="eq-166"></span><span id="eq-167"></span>

```math
\begin{aligned}
O\big((\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I)\big) & \equiv & (\boldsymbol{\sigma}', \boldsymbol{\mu}', A', I) & \qquad \text{(164)} \\
\Delta & \equiv & \mathbf{\alpha}_{w} - \mathbf{\delta}_{w} & \qquad \text{(165)} \\
\lVert\boldsymbol{\mu}'_{\mathbf{s}}\rVert & \equiv & \lVert\boldsymbol{\mu}_{\mathbf{s}}\rVert + \Delta & \qquad \text{(166)} \\
\quad \forall x \in [\mathbf{\alpha}_{w}, \lVert\boldsymbol{\mu}'_{\mathbf{s}}\rVert): \boldsymbol{\mu}'_{\mathbf{s}}[x] & \equiv & \boldsymbol{\mu}_{\mathbf{s}}[x-\Delta] & \qquad \text{(167)}
\end{aligned}
```

gasは命令のgasコストだけ減少し、ほとんどの命令ではプログラム・カウンタが各サイクルで増加する。三つの例外については、二つの命令のいずれかで添字付けされ、対応する値へ評価される関数 $`J`$ を仮定する。

<span id="eq-168"></span><span id="eq-169"></span><span id="eq:mu_pc"></span>

```math
\begin{aligned}
\quad \boldsymbol{\mu}'_{\mathrm{g}} & \equiv & \boldsymbol{\mu}_{\mathrm{g}} - C(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) & \qquad \text{(168)} \\
\quad \boldsymbol{\mu}'_{\mathrm{pc}} & \equiv & \begin{cases}
J_{\text{JUMP}}(\boldsymbol{\mu}) & \text{if} \quad w = \text{JUMP} \\
J_{\text{JUMPI}}(\boldsymbol{\mu}) & \text{if} \quad w = \text{JUMPI} \\
N(\boldsymbol{\mu}_{\mathrm{pc}}, w) & \text{otherwise}
\end{cases} & \qquad \text{(169)}
\end{aligned}
```

一般に、メモリ、累積サブ状態、システム状態は変化しないと仮定する。

<span id="eq-170"></span><span id="eq-171"></span><span id="eq-172"></span><span id="eq-173"></span>

```math
\begin{aligned}
\boldsymbol{\mu}'_{\mathbf{m}} & \equiv & \boldsymbol{\mu}_{\mathbf{m}} & \qquad \text{(170)} \\
\boldsymbol{\mu}'_{\mathrm{i}} & \equiv & \boldsymbol{\mu}_{\mathrm{i}} & \qquad \text{(171)} \\
A' & \equiv & A & \qquad \text{(172)} \\
\boldsymbol{\sigma}' & \equiv & \boldsymbol{\sigma} & \qquad \text{(173)}
\end{aligned}
```

ただし命令は通常、これらの値の一つ以上の構成要素を変更する。命令ごとに変更される構成要素は、 $`\alpha`$ と $`\delta`$ の値およびgas要件の形式的記述とともに[付録H](#app:vm)に記載する。

<span id="ch:pos_transition"></span>

# 10. プルーフ・オブ・ステークへの移行

*Paris* ハードフォークは、Ethereum の基礎となる合意形成機構をプルーフ・オブ・ワークからプルーフ・オブ・ステークへ変更した。

Ethereum のそれ以前のすべてのハードフォークと異なり、*Paris* は特定のブロック高で発生するのではなく、指定された*終端総難易度*への到達後に発生すると定義された。ブロック高ではなく総難易度を用いたのは、少数のハッシュ・パワーが悪意あるフォークを作り、ブロック高要件を先に満たして最初のプルーフ・オブ・ステーク・ブロックを獲得するという状況を避けるためである。

したがって、*Paris* フォークが有効になる前の最後のプルーフ・オブ・ワーク・ブロックである*ターミナル・ブロック*は、次を満たすものとして定義される。

<span id="eq-174"></span><span id="eq-175"></span>

```math
\begin{aligned}
B_{\mathrm{t}} & \geqslant & 58750000000000000000000 & \qquad \text{(174)} \\
P(B_{\mathrm{H}})_{\mathrm{t}} & < & 58750000000000000000000 & \qquad \text{(175)}
\end{aligned}
```

ここで $`B_{\mathrm{t}}`$ はブロック $`B`$ の総難易度、 $`P(B_{\mathrm{H}})_{\mathrm{t}}`$ はその親の総難易度である。

プルーフ・オブ・ワーク（*Paris* 前）のブロック $`B`$ の総難易度を再帰的に次のように定義する。

<span id="eq-176"></span>

```math
\begin{aligned}
B_{\mathrm{t}} & \equiv & P(B_{\mathrm{H}})_{\mathrm{t}} + H_{\mathrm{d}} & \qquad \text{(176)}
\end{aligned}
```

ここで $`H_{\mathrm{d}}`$ は現在のブロック $`B`$ の難易度である。

終端ブロックに到達すると、新しいブロックは Beacon Chain によって処理される。

## 10.1. Paris 後の更新

Beacon Chain は12秒ごとに新しいスロットを生成するため、*Paris* 後の更新は特定のタイムスタンプで発生するよう予定できる。実行レイヤーでは、予定時刻後に生成された最初のブロックで更新が発生する。たとえば *Shanghai* ハードフォークは、エポック194,048の2023-04-12 10:27:35 UTCに発生するよう予定された。バリデータはこのエポックの最初の二つのスロットでブロックを提案できなかったが、スロット6,209,538でバリデータが最終的にブロック17,034,870を提案し、実行レイヤーの *Shanghai* への移行を示した。

<span id="tnref-5"></span>[訳注5](#tn-5)

<span id="ch:blocktree_to_blockchain"></span>

# 11. ブロック木からブロックチェーンへ

*Paris* ハードフォークでプルーフ・オブ・ステークへ移行する以前、正準ブロックチェーンは、[第10節](#ch:pos_transition)で $`B_{\mathrm{t}}`$ として定義した*総難易度*が最大のブロック経路と定義されていた。

[第10節](#ch:pos_transition)で記述した*終端ブロック*への到達後は、最大*総難易度*規則を廃止し、*LMD GHOST* と呼ばれる規則を採用しなければならない[^12]。

*Paris* 後にどのブロックが正準 Ethereum ブロックチェーンを構成するかを決定するには、本稿で記述しない Beacon Chain の追加情報が必要であることに注意されたい。Beacon Chain が発行するイベントを接頭辞 $`\mathtt{POS\_}`$ で表す。

[第10節](#ch:pos_transition)で述べた*遷移ブロック*における最初のイベントを起点として、 $`\mathtt{POS\_FORKCHOICE\_UPDATED}`$ イベントが発生するたびに、正準チェーンはジェネシス・ブロックから始まり、そのイベントがチェーン先頭として指定したブロックで終わるチェーンとして定義される。

$`\mathtt{POS\_FORKCHOICE\_UPDATED}`$ が発行された場合、かつその場合に限りチェーンの先頭を更新し、そのイベントが指定するブロックへ設定する。チェーン先頭を楽観的に更新してはならない。

$`\mathtt{POS\_FORKCHOICE\_UPDATED}`$ イベントはさらに最終化済みブロックを参照する。最新の最終化済みブロックをこのブロックに設定する。

正準ブロックチェーンは、[第10節](#ch:pos_transition)で定義した*終端ブロック*のハッシュと番号を持つブロックも含まなければならない。

<span id="ch:finalisation"></span>

# 12. ブロックの最終化

ブロックの最終化処理には次の3段階がある。

1.  引き出しを実行する。

2.  トランザクションを検証する。

3.  状態を検証する。

## 12.1. 引き出しの実行

ブロックのトランザクションを処理した後、引き出しを実行する。引き出しとは、受取人アカウントの残高を指定された Gwei 量だけ増やすことにすぎない。ほかの残高は減少せず、引き出しは移転ではなく資金の創出である。引き出し操作は失敗せず、gas コストもない。関数 $`E`$ を引き出し状態遷移関数として定義する。

<span id="eq-177"></span><span id="eq-178"></span><span id="eq-179"></span>

```math
\begin{aligned}
E(\boldsymbol{\sigma}_w, W) & \equiv & \boldsymbol{\sigma}_{w+1} & \qquad \text{(177)} \\
\boldsymbol{\sigma}_{w+1} & \equiv & \boldsymbol{\sigma}_w \quad \text{except:} & \qquad \text{(178)} \\
\boldsymbol{\sigma}_{w+1}[W_r]_{\mathrm{b}} & \equiv & \boldsymbol{\sigma}_{w}[W_r]_{\mathrm{b}} + (W_a \times 10^9) & \qquad \text{(179)}
\end{aligned}
```

<div id="Kappa">

</div>

最後に、引き出しに対するブロック水準の状態遷移関数 $`K`$ を定義する。

<span id="eq-180"></span>

```math
K(\boldsymbol{\sigma}, B) \equiv E(E(\boldsymbol{\sigma}, W_0), W_1) ... \qquad \text{(180)}
```

## 12.2. トランザクションの検証

与えられた **gasUsed** は、列挙されたトランザクションと正確に対応しなければならない。ブロック内の総使用gas [$`{B_{\mathrm{H}}}_{\mathrm{g}}`$](#H__g) は、最後のトランザクション時点の累積使用gasに等しくなければならない。

<span id="eq-181"></span>

```math
{B_{\mathrm{H}}}_{\mathrm{g}} = \ell(\mathbf{R})_{\mathrm{u}} \qquad \text{(181)}
```

<span id="sec:statenoncevalidation"></span>

## 12.3. 状態の検証

<div id="Gamma">

</div>

ここで、ブロック $`B`$ をその初期状態へ写す関数 $`\Gamma`$ を定義できる。

<span id="eq-182"></span>

```math
\Gamma(B) \equiv \begin{cases}
\boldsymbol{\sigma}_0 & \text{if} \quad P(B_{\mathrm{H}}) = \varnothing \\
\boldsymbol{\sigma}_{\mathrm{i}}: \mathtt{TRIE}(L_{\mathrm{S}}(\boldsymbol{\sigma}_{\mathrm{i}})) = {P(B_{\mathrm{H}})_{\mathrm{H}}}_{\mathrm{r}} & \text{otherwise}
\end{cases} \qquad \text{(182)}
```

ここで $`\mathtt{TRIE}(L_{\mathrm{S}}(\boldsymbol{\sigma}_{\mathrm{i}}))`$ は状態 $`\boldsymbol{\sigma}_{\mathrm{i}}`$ のトライのルート・ノード・ハッシュを意味する。トライは本質的に不変データ構造であるため、実装はこれを状態データベースに格納すると仮定する。この格納は自明かつ効率的である。

<div id="Phi">

</div>

最後に、不完全なブロック $`B`$ を完全なブロック $`B'`$ へ写すブロック遷移関数 $`\Phi`$ を定義する。

<span id="eq-183"></span><span id="eq-184"></span>

```math
\begin{aligned}
\Phi(B) & \equiv & B': \quad B' = B \quad \text{except:} & \qquad \text{(183)} \\
{B'_{\mathrm{H}}}_{\mathrm{r}} & = & \mathtt{TRIE}(L_{\mathrm{S}}(K(\Pi(\Gamma(B), B), B))) & \qquad \text{(184)}
\end{aligned}
```

本稿の冒頭で述べたように、[$`\Pi`$](#Pi) は状態遷移関数であり、トランザクション評価関数 [$`\Upsilon`$](#Upsilon_state_transition) によって定義される。

前述のとおり、 $`\mathbf{R}[n]_{\mathrm{z}}`$ 、 $`\mathbf{R}[n]_{\mathbf{l}}`$ 、 $`\mathbf{R}[n]_{\mathrm{u}}`$ は、それぞれ第 $`n`$ トランザクション後のステータス・コード、ログ、累積使用gasである（タプルの第4要素 $`\mathbf{R}[n]_{\mathrm{b}}`$ は、すでにログによって定義した）。また第 $`n`$ 状態 $`\boldsymbol{\sigma}[n]`$ を、直前のトランザクションから得られた状態（最初のトランザクションではブロックの初期状態）に対応するトランザクションを適用して得られる状態として単純に定義する。

<span id="eq-185"></span><span id="sigma_n"></span>

```math
\boldsymbol{\sigma}[n] = \begin{cases} \Gamma(B) & \text{if} \quad n < 0 \\ \Upsilon(\boldsymbol{\sigma}[n - 1], B_{\mathbf{T}}[n]) & \text{otherwise} \end{cases} \qquad \text{(185)}
```

$`B_{\mathbf{R}}[n]_{\mathrm{u}}`$ についても同様の方法を採り、各項目を、対応するトランザクションの評価に使用したgasと直前の項目（最初の場合はゼロ）との和として定義し、累計値を得る。

<span id="eq-186"></span>

```math
\mathbf{R}[n]_{\mathrm{u}} = \begin{cases} 0 & \text{if} \quad n < 0 \\
\begin{array}{l}
\Upsilon^g(\boldsymbol{\sigma}[n - 1], B_{\mathbf{T}}[n])\\ \quad + \mathbf{R}[n-1]_{\mathrm{u}}
\end{array}
 & \text{otherwise} \end{cases} \qquad \text{(186)}
```

$`\mathbf{R}[n]_{\mathbf{l}}`$ については、トランザクション実行関数で定義した [$`\Upsilon^{\mathbf{l}}`$](#Upsilon_pow_l) 関数を用いる。

<span id="eq-187"></span>

```math
\mathbf{R}[n]_{\mathbf{l}} =
\Upsilon^{\mathbf{l}}(\boldsymbol{\sigma}[n - 1], B_{\mathbf{T}}[n]) \qquad \text{(187)}
```

[$`\mathbf{R}[n]_{\mathrm{z}}`$](#Upsilon_pow_z) も同様に定義する。

<span id="eq-188"></span>

```math
\mathbf{R}[n]_{\mathrm{z}} =
\Upsilon^{\mathrm{z}}(\boldsymbol{\sigma}[n - 1], B_{\mathbf{T}}[n]) \qquad \text{(188)}
```

<div id="Pi">

</div>

最後に、 $`\Pi`$ を最終トランザクションの結果状態 $`\ell(\boldsymbol{\sigma})`$ として定義する。

<span id="eq-189"></span>

```math
\Pi(\boldsymbol{\sigma}, B) \equiv \ell(\boldsymbol{\sigma}) \qquad \text{(189)}
```

以上により、（合意形成前の）完全なブロック遷移機構が定義された。

# 13. コントラクトの実装

特定の有用な動作を可能にするコントラクト工学上のパターンがいくつかある。ここではそのうち、データ・フィードと乱数を簡潔に論じる。

## 13.1. データ・フィード

データ・フィード・コントラクトは、Ethereum 内から外部世界の情報へアクセスできるようにするという単一のサービスを提供する。この情報の正確性と適時性は保証されず、個々のデータ・フィードをどの程度信頼できるかの判断は、それを利用する二次コントラクトの作者に委ねられる。

一般的なパターンでは、Ethereum 内の一つのコントラクトがメッセージ呼び出しを受けると、外部現象に関する適時の情報を返す。例としてニューヨーク市の現地気温がある。これはストレージ内の既知の位置の値を返すコントラクトとして実装できる。当然、この位置は正しい気温で維持する必要がある。そのためパターンの第2部分では、外部サーバが Ethereum ノードを実行し、新しいブロックを発見すると直ちに、当該ストレージ値を更新する有効なトランザクションを作成してコントラクトへ送信する。コントラクトのコードは、そのサーバに保持された識別情報からの更新だけを受け入れる。

## 13.2. 乱数

決定論的システム内で乱数を提供することは、当然ながら不可能である。しかし、トランザクション時には通常知り得ないデータを用いて擬似乱数で近似できる。このデータにはブロック・ハッシュやブロックの受益者アドレスなどがある。悪意あるバリデータがこれらの値を制御しにくくするには、[BLOCKHASH](#blockhash) 演算により過去256ブロックのハッシュを擬似乱数として利用すべきである。このような数の列には、ある定数を加えて結果をハッシュするという自明な解がある。

<span id="ch:future"></span>

# 14. 将来の方向性

状態データベースは将来にわたって過去のすべての状態[トライ](#trie)構造を維持する必要はない。各ノードの経過期間を管理し、十分に新しくもチェックポイントでもないノードは最終的に破棄すべきである。チェックポイント、すなわち特定ブロックの状態トライを走査できるデータベース内ノード集合を用いれば、ブロックチェーン全体の任意状態を取得するために必要な計算量へ上限を設けられる。

ブロックチェーンの統合を用いれば、クライアントがフルノードとして機能するためにダウンロードすべきブロック数を削減できる。所定の時点（たとえば1万ブロックごと）のトライ構造の圧縮アーカイブをピア・ネットワークが維持し、実質的に[ジェネシス・ブロック](#Genesis_Block)を再設定できる。これにより、ダウンロード量を単一のアーカイブと、厳格な上限数のブロックにまで減らせる。

最後に、ブロックチェーン圧縮も行い得る。一定数のブロックにわたってトランザクションを送受信していない状態トライのノードを破棄し、Ether の漏出と状態データベースの成長の双方を抑えられる。

<span id="ch:conclusion"></span>

# 15. 結論

本稿では Ethereum のプロトコルを導入し、論じ、形式的に定義した。このプロトコルに基づき、読者は Ethereum ネットワーク上のノードを実装し、分散化された安全な社会的オペレーティング・システムへほかの参加者とともに加われる。相互作用の規則をアルゴリズム的に規定し、自律的に執行するためのコントラクトを作成できる。

# 16. 謝辞

*Homestead* 改訂を執筆した Aeron Buchanan、Ethash アルゴリズムを執筆した Christoph Jentzsch、EIP-150 の変更の大部分を行った Yoichi Hirai に深く感謝する。重要な保守、有用な訂正および提案は、Gustav Simonsson、Paweł Bylica、Jutta Steiner、Nick Savers、Viktor Trón、Marko Simovic、Giacomo Tazzari、そしてもちろん Vitalik Buterin を含む、Ethereum DEV 組織および Ethereum コミュニティ全体の多くの人々から提供された。

# 17. 入手先

本稿のソースは <https://github.com/ethereum/yellowpaper/> で保守されている。自動生成 PDF は <https://ethereum.github.io/yellowpaper/paper.pdf> にある。

# 参考文献

<div id="refs" class="references csl-bib-body hanging-indent">

<div id="ref-aron2012bitcoin" class="csl-entry">

Aron, Jacob. 2012. “<span class="nocase">BitCoin software finds new life</span>.” *New Scientist* 213 (2847): 20. <http://www.sciencedirect.com/science/article/pii/S0262407912601055>.

</div>

<div id="ref-back2002hashcash" class="csl-entry">

Back, Adam. 2002. “Hashcash - Amortizable Publicly Auditable Cost-Functions.” <http://www.hashcash.org/papers/amortizable.pdf>.

</div>

<div id="ref-EIP-3541" class="csl-entry">

Beregszaszi, Alex, Paweł Bylica, Andrei Maiboroda, Alexey Akhunov, Christian Reitwiessner, and Martin Swende. 2021. “EIP-3541: Reject New Contract Code Starting with the 0xEF Byte.” <https://eips.ethereum.org/EIPS/eip-3541>.

</div>

<div id="ref-Keccak" class="csl-entry">

Bertoni, Guido, Joan Daemen, Michaël Peeters, and Gilles Van Assche. 2011. “<span class="nocase">The KECCAK SHA-3 submission</span>.” <https://keccak.team/files/Keccak-submission-3.pdf>.

</div>

<div id="ref-boutellier2014pirates" class="csl-entry">

Boutellier, Roman, and Mareike Heinzen. 2014. “<span class="nocase">Pirates, Pioneers, Innovators and Imitators</span>.” In *Growth Through Innovation*, 85–96. Springer. <https://www.springer.com/gb/book/9783319040158>.

</div>

<div id="ref-buterin2013ethereum" class="csl-entry">

Buterin, Vitalik. 2013. “<span class="nocase">Ethereum: A Next-Generation Smart Contract and Decentralized Application Platform</span>.” <https://github.com/ethereum/wiki/wiki/White-Paper>.

</div>

<div id="ref-EIP-2" class="csl-entry">

———. 2015. “EIP-2: Homestead Hard-Fork Changes.” <https://eips.ethereum.org/EIPS/eip-2>.

</div>

<div id="ref-EIP-155" class="csl-entry">

———. 2016. “EIP-155: Simple Replay Attack Protection.” <https://eips.ethereum.org/EIPS/eip-155>.

</div>

<div id="ref-EIP-1014" class="csl-entry">

———. 2018. “EIP-1014: Skinny CREATE2.” <https://eips.ethereum.org/EIPS/eip-1014>.

</div>

<div id="ref-EIP-1559" class="csl-entry">

Buterin, Vitalik, Eric Conner, Rick Dudley, Matthew Slipper, Ian Norden, and Abdelhamid Bakhta. 2019. “EIP-1559: Fee Market Change for ETH 1.0 Chain.” <https://eips.ethereum.org/EIPS/eip-1559>.

</div>

<div id="ref-EIP-2929" class="csl-entry">

Buterin, Vitalik, and Martin Swende. 2020a. “EIP-2929: Gas Cost Increases for State Access Opcodes.” <https://eips.ethereum.org/EIPS/eip-2929>.

</div>

<div id="ref-EIP-2930" class="csl-entry">

———. 2020b. “EIP-2930: Optional Access Lists.” <https://eips.ethereum.org/EIPS/eip-2930>.

</div>

<div id="ref-EIP-3529" class="csl-entry">

———. 2021. “EIP-3529: Reduction in Refunds.” <https://eips.ethereum.org/EIPS/eip-3529>.

</div>

<div id="ref-Courtois2014" class="csl-entry">

Courtois, Nicolas T., Marek Grajek, and Rahul Naik. 2014. “Optimizing SHA256 in Bitcoin Mining.” In *Cryptography and Security Systems: Third International Conference, CSS 2014, Lublin, Poland, September 22-24, 2014. Proceedings*, edited by Zbigniew Kotulski, Bogdan Księżopolski, and Katarzyna Mazur, 131–44. Berlin, Heidelberg: Springer Berlin Heidelberg. <https://doi.org/10.1007/978-3-662-44893-9_12>.

</div>

<div id="ref-Davey2002_zbMATH01748069" class="csl-entry">

Davey, B. A., and H. A. Priestley. 2002. *Introduction to Lattices and Order. 2nd Ed.* 2nd ed. Cambridge: Cambridge University Press.

</div>

<div id="ref-dwork92pricingvia" class="csl-entry">

Dwork, Cynthia, and Moni Naor. 1992. “Pricing via Processing or Combatting Junk Mail.” In *In 12th Annual International Cryptology Conference*, 139–47. <http://www.wisdom.weizmann.ac.il/~naor/PAPERS/pvp.pdf>.

</div>

<div id="ref-EIP-3607" class="csl-entry">

Feist, Dankrad, Dmitry Khovratovich, and Marius van der Wijden. 2021. “EIP-3607: Reject Transactions from Senders with Deployed Code.” <https://eips.ethereum.org/EIPS/eip-3607>.

</div>

<div id="ref-FowlerNollVo1991FNVHash" class="csl-entry">

Glenn Fowler, Phong Vo, Landon Curt Noll. 1991. “<span class="nocase">Fowler–Noll–Vo hash function</span>.” <http://www.isthe.com/chongo/tech/comp/fnv/index.html>.

</div>

<div id="ref-gura2004comparing" class="csl-entry">

Gura, Nils, Arun Patel, Arvinderpal Wander, Hans Eberle, and Sheueling Chang Shantz. 2004. “Comparing Elliptic Curve Cryptography and RSA on 8-Bit CPUs.” In *Cryptographic Hardware and Embedded Systems-CHES 2004*, 119–32. Springer. <https://www.iacr.org/archive/ches2004/31560117/31560117.pdf>.

</div>

<div id="ref-EIP-152" class="csl-entry">

Hess, Tjaden, Matt Luongo, Piotr Dyraga, and James Hancock. 2016. “EIP-152: Add BLAKE2 Compression Function ‘F‘ Precompile.” <https://eips.ethereum.org/EIPS/eip-152>.

</div>

<div id="ref-ECDSAcerticom" class="csl-entry">

Johnson, Don, Alfred Menezes, and Scott Vanstone. 2001. “The Elliptic Curve Digital Signature Algorithm (ECDSA).” Canada: Certicom Research. Accessed 21 September 2017, but the original link was inaccessible on 19 October 2017. Refer to section 6.2 for ECDSAPUBKEY, and section 7 for ECDSASIGN and ECDSARECOVER. <https://web.archive.org/web/20170921160141/http://cs.ucsb.edu/~koc/ccs130h/notes/ecdsa-cert.pdf>.

</div>

<div id="ref-lerner2014randmemohash" class="csl-entry">

Lerner, Sergio Demian. 2014. “Strict Memory Hard Hashing Functions.” <http://www.hashcash.org/papers/memohash.pdf>.

</div>

<div id="ref-miller1997future" class="csl-entry">

Miller, Mark. 1997. “<span class="nocase">The Future of Law</span>.” In *<span class="nocase">paper delivered at the Extro 3 Conference (August 9)</span>*. <https://drive.google.com/file/d/0Bw0VXJKBgYPMS0J2VGIyWWlocms/edit?usp=sharing>.

</div>

<div id="ref-nakamoto2008bitcoin" class="csl-entry">

Nakamoto, Satoshi. 2008. “<span class="nocase">Bitcoin: A peer-to-peer electronic cash system</span>.” <http://www.bitcoin.org/bitcoin.pdf>.

</div>

<div id="ref-colouredcoins2012rosenfeld" class="csl-entry">

Rosenfeld, Meni, Yoni Assia, Vitalik Buterin, m liorhakiLior, Oded Leiba, Assaf Shomer, and Eliran Zach. 2012. “Colored Coins Protocol Specification.” <https://github.com/Colored-Coins/Colored-Coins-Protocol-Specification>.

</div>

<div id="ref-RFC-7693" class="csl-entry">

Saarinen, Markku–Juhani, and Jean–Philippe Aumasson. 2015. “RFC 7693: The BLAKE2 Cryptographic Hash and Message Authentication Code (MAC).” <https://tools.ietf.org/html/rfc7693>.

</div>

<div id="ref-sprankel2013technical" class="csl-entry">

Sprankel, Simon. 2013. “<span class="nocase">Technical Basis of Digital Currencies</span>.” <http://www.coderblog.de/wp-content/uploads/technical-basis-of-digital-currencies.pdf>.

</div>

<div id="ref-szabo1997formalizing" class="csl-entry">

Szabo, Nick. 1997. “<span class="nocase">Formalizing and securing relationships on public networks</span>.” *First Monday* 2 (9). <http://firstmonday.org/ojs/index.php/fm/article/view/548>.

</div>

<div id="ref-EIP-2200" class="csl-entry">

Tang, Wei. 2019. “EIP-2200: Structured Definitions for Net Gas Metering.” <https://eips.ethereum.org/EIPS/eip-2200>.

</div>

<div id="ref-vishnumurthy03karma:a" class="csl-entry">

Vishnumurthy, Vivek, Sangeeth Chandrakumar, and Emin Gün Sirer. 2003. “KARMA: A Secure Economic Framework for Peer-to-Peer Resource Sharing.” <https://www.cs.cornell.edu/people/egs/papers/karma.pdf>.

</div>

<div id="ref-mastercoin2013willett" class="csl-entry">

Willett, J. R. 2013. “MasterCoin Complete Specification.” <https://github.com/mastercoin-MSC/spec>.

</div>

<div id="ref-EIP-2718" class="csl-entry">

Zoltu, Micah. 2020. “EIP-2718: Typed Transaction Envelope.” <https://eips.ethereum.org/EIPS/eip-2718>.

</div>

</div>

<span id="ch:Terminology"></span>

# 付録A. 用語集

外部主体（External Actor）
: Ethereum ノードと接続できるが、Ethereum 世界の外部にある人またはその他の実体。署名済みトランザクションを投入し、ブロックチェーンと関連状態を調べることで Ethereum と相互作用できる。一つ以上の固有アカウントを持つ。

アドレス（Address）
: アカウントの識別に用いる160ビット・コード。

アカウント（Account）
: アカウントは、Ethereum 状態の一部として維持される固有の残高とトランザクション数を持つ。さらに、いずれも空である可能性のある EVM コードとストレージ状態が関連付けられる。同質ではあるが、実用上は二つの型を区別するのが妥当である。関連 EVM コードが空であり、残高が制御されるとすれば何らかの外部実体によって制御されるアカウントと、関連 EVM コードが空でなく、自律オブジェクトを表すアカウントである。各アカウントは識別用のアドレスを一つ持つ。

トランザクション（Transaction）
: 外部主体が署名したデータ片。メッセージまたは新しい自律オブジェクトを表す。トランザクションはブロックチェーンの各ブロックに記録される。

自律オブジェクト（Autonomous Object）
: Ethereum の仮想的状態内にのみ存在する概念上のオブジェクト。固有アドレスを持ち、したがって関連アカウントを持つ。そのアカウントには空でない EVM コードが関連付けられる。当該アカウントのストレージ状態としてのみ組み込まれる。

ストレージ状態（Storage State）
: 所与のアカウントに固有であり、そのアカウントに関連付けられた EVM コードの実行と次の実行の間に維持される情報。

メッセージ（Message）
: 自律オブジェクトの決定論的演算またはトランザクションの暗号学的に安全な署名を通じて、二つのアカウント間で渡されるデータ（バイト集合）と値（Ether で指定）。

メッセージ呼び出し（Message Call）
: あるアカウントから別のアカウントへメッセージを渡す行為。宛先アカウントに空でない EVM コードが関連付けられていれば、当該オブジェクトの状態で VM を起動してメッセージを処理する。メッセージ送信者が自律オブジェクトであれば、呼び出しは VM 演算から返されたデータを渡す。

Gas
: ネットワークの基本コスト単位。（PoC-4 時点では）Ether のみで支払い、必要に応じて Gas と自由に相互変換される。Gas は Ethereum の内部計算エンジン外には存在しない。価格はトランザクションによって設定され、バリデータは Gas 価格が低すぎるトランザクションを自由に無視できる。

コントラクト（Contract）
: アカウントに関連付け得る EVM コード片と自律オブジェクトの双方を意味する非形式的用語。

オブジェクト（Object）
: 自律オブジェクトの同義語。

アプリ（App）
: Ethereum Browser 内でホストされ、エンドユーザーに見えるアプリケーション。

Ethereum Browser
: （別名 Ethereum Reference Client）簡略化されたブラウザ（Chrome など）に似たクロスプラットフォーム GUI であり、バックエンドが純粋に Ethereum プロトコル上にあるサンドボックス化アプリケーションをホストできる。

Ethereum 仮想マシン
: （別名 EVM）アカウントに関連付けられた EVM コードの実行モデルで中核をなす仮想マシン。

Ethereum 実行時環境
: （別名 ERE）EVM 内で実行される自律オブジェクトに提供される環境。EVM に加え、CALL や CREATE を含む一部の入出力命令について EVM が依存するワールド状態の構造を含む。

EVM コード
: EVM がネイティブに実行できるバイトコード。アカウントへのメッセージの意味と影響を形式的に規定するために用いる。

EVM アセンブリ
: 人間が読める形式の EVM コード。

LLL
: Lisp に似た低水準言語（Lisp-like Low-level Language）。単純なコントラクトを書くために用いる人間が記述可能な言語であり、トランスコンパイル先となる汎用低水準言語ツールキットでもある。

<span id="app:rlp"></span>

# 付録B. 再帰的長さ接頭辞

<div id="rlp">

</div>

これは、任意構造のバイナリ・データ（バイト配列）を符号化する直列化方式である。

可能な構造の集合 $`\mathbb{T}`$ を次のように定義する。

<span id="eq-190"></span><span id="eq-191"></span><span id="eq-192"></span>

```math
\begin{aligned}
\mathbb{T} & \equiv & \mathbb{L} \uplus \mathbb{B} & \qquad \text{(190)} \\
\mathbb{L} & \equiv & \{ \mathbf{t}: \mathbf{t} = ( \mathbf{t}[0], \mathbf{t}[1], ... ) \; \wedge \; \forall n < \lVert \mathbf{t} \rVert : \mathbf{t}[n] \in \mathbb{T} \} & \qquad \text{(191)} \\
\mathbb{B} & \equiv & \{ \mathbf{b}: \mathbf{b} = ( \mathbf{b}[0], \mathbf{b}[1], ... ) \; \wedge \; \forall n < \lVert \mathbf{b} \rVert : \mathbf{b}[n] \in \mathbb{O} \} & \qquad \text{(192)}
\end{aligned}
```

ここで $`\mathbb{O}`$ は（8ビット）バイトの集合である。したがって $`\mathbb{B}`$ はすべてのバイト列（バイト配列とも呼ばれ、木として考えれば葉）の集合、 $`\mathbb{L}`$ は単一の葉ではないすべての木状（部分）構造（木として考えれば分岐ノード）の集合、 $`\mathbb{T}`$ はすべてのバイト配列およびそのような構造列の集合である。非交和 $`\uplus`$ が必要なのは、空バイト配列 $`()\in\mathbb{B}`$ と空リスト $`()\in\mathbb{L}`$ を区別するためだけである。両者は後述の定義どおり異なる方法で符号化される。慣例に従い、記法を濫用して非交和の添字を省略し、文脈から推論できるものとする。

RLP関数 $`\mathtt{RLP}`$ を二つの補助関数によって定義する。一つ目は値がバイト配列の場合を、二つ目は値がさらに値を含む列である場合を扱う。

<span id="eq-193"></span>

```math
\mathtt{RLP}(\mathbf{x}) \equiv \begin{cases} R_{\mathrm{b}}(\mathbf{x}) & \text{if} \quad \mathbf{x} \in \mathbb{B} \\ R_{\mathrm{l}}(\mathbf{x}) & \text{otherwise} \end{cases} \qquad \text{(193)}
```

<div id="RLP_serialisation_of_a_byte_array_R__b_word_def">

</div>

直列化する値がバイト配列の場合、RLP 直列化は次の3形式のいずれかをとる。

- バイト配列が単一のバイトだけを含み、そのバイトが128未満なら、入力は出力と厳密に等しい。

- バイト配列が56バイト未満なら、出力は入力の前に、バイト配列長に128を加えた値に等しいバイトを付けたものとなる。

- それ以外では、入力が $`2^{64}`$ バイト未満である場合、入力の前に、ビッグエンディアン整数として解釈すると入力バイト配列長に等しくなる最小長バイト配列を付け、さらにその前に、この長さ値を忠実に符号化するために必要なバイト数に183を加えた値を付けたものが出力となる。

$`2^{64}`$ バイト以上のバイト配列は符号化できない。この制限により、バイト配列の符号化の先頭バイトは常に192未満となり、 $`\mathbb{L}`$ の列の符号化と容易に区別できる。

<div id="RLP_serialisation_of_a_byte_array_R__b_math_def">

</div>

形式的には、 $`R_{\mathrm{b}}`$ を次のように定義する。

<span id="eq-194"></span><span id="eq-195"></span><span id="eq-196"></span><span id="eq:BE"></span>

```math
\begin{aligned}
R_{\mathrm{b}}(\mathbf{x}) & \equiv & \begin{cases}
\mathbf{x} & \text{if} \quad \lVert \mathbf{x} \rVert = 1 \wedge \mathbf{x}[0] < 128 \\
(128 + \lVert \mathbf{x} \rVert) \cdot \mathbf{x} & \text{else if} \quad \lVert \mathbf{x} \rVert < 56 \\
\big(183 + \big\lVert \mathtt{BE}(\lVert \mathbf{x} \rVert) \big\rVert \big) \cdot \mathtt{BE}(\lVert \mathbf{x} \rVert) \cdot \mathbf{x} & \text{else if} \quad \lVert \mathbf{x} \rVert < 2^{64} \\
\varnothing & \text{otherwise}
\end{cases} & \qquad \text{(194)} \\
\mathtt{BE}(x) & \equiv & (b_0, b_1, ...): b_0 \neq 0 \wedge x = \sum_{n = 0}^{\lVert \mathbf{b} \rVert - 1} b_n \cdot 256^{\lVert \mathbf{b} \rVert - 1 - n} & \qquad \text{(195)} \\
(x_1, ..., x_n) \cdot (y_1, ..., y_m) & = & (x_1, ..., x_n, y_1, ..., y_m) & \qquad \text{(196)}
\end{aligned}
```

したがって $`\mathtt{BE}`$ は、非負整数値を最小長のビッグエンディアン・バイト配列へ展開する関数であり、ドット演算子は列の連結を行う。

<div id="RLP_serialisation_of_a_sequence_of_other_items_R__l_word_def">

</div>

一方、直列化する値がほかの項目の列である場合、RLP 直列化は次の2形式のいずれかをとる。

- 各項目の直列化を連結した長さが56バイト未満なら、出力はその連結結果の前に、そのバイト配列長に192を加えた値に等しいバイトを付けたものとなる。

- それ以外では、連結した直列化が $`2^{64}`$ バイト未満である場合、その前に、ビッグエンディアン整数として解釈すると連結済み直列化バイト配列長に等しくなる最小長バイト配列を付け、さらにその前に、この長さ値を忠実に符号化するために必要なバイト数に247を加えた値を付けたものが出力となる。

連結した直列化項目が $`2^{64}`$ バイト以上となる列は符号化できない。この制限により、符号化の先頭バイトは255を超えない（超えればバイトではなくなる）。

<div id="RLP_serialisation_of_a_sequence_of_other_items_R__l_math_def">

</div>

以上から、最後に $`R_{\mathrm{l}}`$ を形式的に定義する。

<span id="eq-197"></span><span id="eq-198"></span>

```math
\begin{aligned}
R_{\mathrm{l}}(\mathbf{x}) & \equiv & \begin{cases}
(192 + \lVert s(\mathbf{x}) \rVert) \cdot s(\mathbf{x}) & \text{if} \quad s(\mathbf{x}) \neq \varnothing \wedge \lVert s(\mathbf{x}) \rVert < 56 \\
\big(247 + \big\lVert \mathtt{BE}(\lVert s(\mathbf{x}) \rVert) \big\rVert \big) \cdot \mathtt{BE}(\lVert s(\mathbf{x}) \rVert) \cdot s(\mathbf{x}) & \text{else if} \quad s(\mathbf{x}) \neq \varnothing \wedge \lVert s(\mathbf{x}) \rVert < 2^{64} \\
\varnothing & \text{otherwise}
\end{cases} & \qquad \text{(197)} \\
s(\mathbf{x}) & \equiv & \begin{cases}
\mathtt{RLP}(\mathbf{x}[0]) \cdot \mathtt{RLP}(\mathbf{x}[1]) \cdot ... & \text{if} \quad \forall i: \mathtt{RLP}(\mathbf{x}[i]) \neq \varnothing \\
\varnothing & \text{otherwise}
\end{cases} & \qquad \text{(198)}
\end{aligned}
```

非負整数（ $`\mathbb{N}`$ 、または任意の $`x`$ に対する $`\mathbb{N}_x`$ ）としてのみ定義されるスカラーをRLPで符号化する場合、ビッグエンディアンとして解釈するとそのスカラーになる最短のバイト配列として符号化しなければならない。したがって、非負整数 $`i`$ のRLPを次のように定義する。

<span id="eq-199"></span>

```math
\mathtt{RLP}(i : i \in \mathbb{N}) \equiv \mathtt{RLP}(\mathtt{BE}(i)) \qquad \text{(199)}
```

RLPデータの解釈時に、スカラーとして復号されるべき断片のバイト列に先頭ゼロが見つかった場合、クライアントはそれを非正準とみなし、ほかの無効なRLPデータと同様に完全に棄却しなければならない。

符号付き値または浮動小数点値について、特定の正準符号化形式はない。

<span id="app:hexprefix"></span>

# 付録C. 16進接頭辞符号化

16進接頭辞符号化は、任意個数のニブルをバイト配列として符号化する効率的な方法である。追加のフラグを格納でき、この方式が用いられる唯一の文脈であるトライにおいて、ノード型の曖昧さを解消する。

これは、ニブル列（集合 $`\mathbb{Y}`$ で表す）とブール値を、バイト列（集合 $`\mathbb{B}`$ で表す）へ写す関数 $`\mathtt{HP}`$ として定義される。

<span id="eq-200"></span><span id="eq-201"></span>

```math
\begin{aligned}
\mathtt{HP}(\mathbf{x}, t): \mathbf{x} \in \mathbb{Y} & \equiv & \begin{cases}
(16f(t), 16\mathbf{x}[0] + \mathbf{x}[1], 16\mathbf{x}[2] + \mathbf{x}[3], ...) &
\text{if} \quad \lVert \mathbf{x} \rVert \; \text{is even} \\
(16(f(t) + 1) + \mathbf{x}[0], 16\mathbf{x}[1] + \mathbf{x}[2], 16\mathbf{x}[3] + \mathbf{x}[4], ...) &
\text{otherwise}
\end{cases} & \qquad \text{(200)} \\
f(t) & \equiv & \begin{cases} 2 & \text{if} \quad t \neq 0 \\ 0 & \text{otherwise} \end{cases} & \qquad \text{(201)}
\end{aligned}
```

したがって、先頭バイトの上位ニブルには二つのフラグが含まれる。最下位ビットは長さが奇数であることを符号化し、次のビットはフラグ $`t`$ を符号化する。先頭バイトの下位ニブルは、ニブル数が偶数の場合はゼロ、奇数の場合は最初のニブルとなる。残るニブルはすべて（この時点では偶数個）、残りのバイトへ適切に収まる。

<span id="app:trie"></span>

# 付録D. 修正 Merkle Patricia 木

<div id="trie">

</div>

修正Merkle Patricia木（トライ）は、任意長のバイナリ・データ（バイト配列）間を対応付ける永続データ構造を提供する。これは、256ビットのバイナリ断片と任意長のバイナリ・データを対応付ける可変データ構造によって定義され、通常はデータベースとして実装される。トライの中核であり、プロトコル仕様上の唯一の要件は、与えられたキー／値ペア集合を識別する単一の値を提供することである。その値は32バイト列または空バイト列のいずれかとなる。プロトコルを有効かつ効率的に実現できるようトライ構造を格納・維持する方法は、実装上の考慮事項に委ねられる。

形式的には、一意なキーを持つバイト列のペアを含む集合である入力値 $`\mathfrak{I}`$ を仮定する。

<span id="eq-202"></span>

```math
\mathfrak{I} = \{ (\mathbf{k}_0 \in \mathbb{B}, \mathbf{v}_0 \in \mathbb{B}), (\mathbf{k}_1 \in \mathbb{B}, \mathbf{v}_1 \in \mathbb{B}), ... \} \qquad \text{(202)}
```

このような列を考える際、タプルのキーまたは値を参照するため、一般的な数値添字記法を用いる。

<span id="eq-203"></span>

```math
\forall I \in \mathfrak{I}: I \equiv (I_0, I_1) \qquad \text{(203)}
```

任意のバイト列は、エンディアンを指定する記法があれば自明にニブル列ともみなせる。ここではビッグエンディアンを仮定する。したがって、

<span id="eq-204"></span><span id="eq-205"></span>

```math
\begin{aligned}
y(\mathfrak{I}) & = & \{ (\mathbf{k}_0' \in \mathbb{Y}, \mathbf{v}_0 \in \mathbb{B}), (\mathbf{k}_1' \in \mathbb{Y}, \mathbf{v}_1 \in \mathbb{B}), ... \} & \qquad \text{(204)} \\
\forall n: \quad \forall i < 2\lVert\mathbf{k}_{n}\rVert: \quad \mathbf{k}_{n}'[i] & \equiv &
\begin{cases}
\lfloor \mathbf{k}_{n}[i \div 2] \div 16 \rfloor & \text{if} \; i \; \text{is even} \\
\mathbf{k}_{n}[\lfloor i \div 2 \rfloor] \bmod 16 & \text{otherwise}
\end{cases} & \qquad \text{(205)}
\end{aligned}
```

この構造で符号化したときに当該集合を表すトライのルートへ評価される関数 $`\texttt{TRIE}`$ を定義する。

<span id="eq-206"></span>

```math
\texttt{TRIE}(\mathfrak{I}) \equiv \texttt{KEC}\big(\texttt{RLP} (c(\mathfrak{I}, 0))\big) \qquad \text{(206)}
```

さらに、トライのノード・キャップ関数 $`n`$ を仮定する。ノードを構成するとき、RLPを用いて構造を符号化する。ストレージの複雑さを減らすため、構成後のRLPが32バイト未満のノードは直接格納し、それ以外のノードについては、そのKeccak-256ハッシュが参照値へ評価されるバイト配列が既知であるとする。したがって、ノード構成関数 $`c`$ によって次のように定義する。

<span id="eq-207"></span>

```math
n(\mathfrak{I}, i) \equiv \begin{cases}
() \in \mathbb{B} & \text{if} \quad \mathfrak{I} = \varnothing \\
c(\mathfrak{I}, i) & \text{if} \quad \lVert \, \texttt{RLP} \big( c(\mathfrak{I}, i) \big) \rVert < 32 \\
\texttt{KEC}\big(\texttt{RLP}( c(\mathfrak{I}, i)) \big) & \text{otherwise}
\end{cases} \qquad \text{(207)}
```

基数木と同様に、トライをルートから葉まで走査すると単一のキー／値ペアを構築できる。走査中、各分岐ノードから一つのニブルを取得してキーを累積する（基数木と同様である）。基数木と異なり、複数のキーが同じ接頭辞を共有する場合、または単一のキーが一意な接尾辞を持つ場合には、二種類の最適化ノードが提供される。したがって走査中、残る二つのノード型である拡張ノードと葉ノードからは、複数のニブルを取得する可能性がある。トライには三種類のノードがある。

Leaf
: 二要素の構造であり、第1要素は、ルートから走査したキーと分岐の累積によってまだ処理されていないキー内のニブルに対応する。16進接頭辞符号化方式を用い、関数の第2引数は1でなければならない。

Extension
: 二要素の構造であり、第1要素は、ルートからの走査でニブルと分岐のキーを累積した部分より先にある、少なくとも二つの異なるキーに共有される長さ1超のニブル列に対応する。16進接頭辞符号化方式を用い、関数の第2引数は0でなければならない。

Branch
: 17項目からなる構造であり、最初の16項目は、キーの走査におけるこの地点で取り得る16通りのニブル値のそれぞれに対応する。17番目の項目は、これが終端ノードであり、したがってキーの走査がこの地点で終了する場合に用いられる。

したがって分岐は必要な場合にのみ用いられ、非ゼロ項目を一つしか含まない分岐ノードは存在してはならない。この構造を、構造構成関数 $`c`$ によって形式的に定義できる。

<span id="eq-208"></span>

```math
c(\mathfrak{I}, i) \equiv \begin{cases}
 \big(\texttt{HP}(I_0[i .. (\lVert I_0\rVert - 1)], 1), I_1 \big) & \text{if} \quad \lVert \mathfrak{I} \rVert = 1 \quad \text{where} \; \exists I: I \in \mathfrak{I} \\
\big(\texttt{HP}(I_0[i .. (j - 1)], 0), n(\mathfrak{I}, j) \big) & \text{if} \quad i \ne j \quad \text{where} \; j = \max \{ x : \exists \mathbf{l}: \lVert \mathbf{l} \rVert = x \wedge \forall I \in \mathfrak{I}: I_0[0 .. (x - 1)] = \mathbf{l} \} \\
(u(0), u(1), ..., u(15), v) & \text{otherwise} \quad \text{where} \begin{array}{rcl}
u(j) & \equiv & n(\{ I : I \in \mathfrak{I} \wedge I_0[i] = j \}, i + 1) \\
v & = & \begin{cases}
I_1 & \text{if} \quad \exists I: I \in \mathfrak{I} \wedge \lVert I_0 \rVert = i \\
() \in \mathbb{B} & \text{otherwise}
\end{cases}
\end{array}
\end{cases} \qquad \text{(208)}
```

## D.1. トライ・データベース

したがって、どのデータを格納し何を格納しないかは実装固有の考慮事項であるため、明示的な仮定を置かない。キー／値集合 $`\mathfrak{I}`$ を32バイト・ハッシュへ写す識別関数を定義し、任意の $`\mathfrak{I}`$ についてそのようなハッシュが一つだけ存在すると規定するだけである。これは厳密には真ではないものの、Keccakハッシュの衝突耐性を考えれば許容可能な精度で正しい。実際には、適切な実装が各集合についてトライのルート・ハッシュを完全に再計算することはない。

適切な実装は、さまざまなトライの計算から得られたノードのデータベースを維持する。より形式的には関数 $`c`$ をメモ化する。この戦略はトライの性質を利用して、以前の任意のキー／値集合の内容を容易に復元するとともに、複数の集合を非常に効率よく格納する。依存関係により、所与のルート・ハッシュを持つトライ内に特定の葉が必ず存在することを示すMerkle証明を、 $`O(\log N)`$ の空間要件で構成できる。

<span id="app:precompiled"></span>

# 付録E. プリコンパイル済みコントラクト

各プリコンパイル済みコントラクトについて、gas不足検査を実装するテンプレート関数 $`\Xi_{\mathtt{PRE}}`$ を用いる。

<span id="eq-209"></span><span id="eq:pre"></span>

```math
\Xi_{\mathtt{PRE}}(\boldsymbol{\sigma}, g, A, I) \equiv \begin{cases}
(\varnothing, 0, A, ()) & \text{if} \quad g < g_{\mathrm{r}} \\
(\boldsymbol\sigma, g - g_{\mathrm{r}}, A, \mathbf{o}) & \text{otherwise}\end{cases} \qquad \text{(209)}
```

各プリコンパイル済みコントラクトはこれらの定義を用い、 $`\mathbf{o}`$ （出力データ）とgas要件 $`g_{\mathrm{r}}`$ の仕様を与える。

$`\Xi_{\mathtt{ECREC}}`$ を、楕円曲線デジタル署名アルゴリズム（ECDSA）の公開鍵復元関数（ecrecover）のプリコンパイル済みコントラクトとして定義する。関数 $`\mathtt{ECDSARECOVER}`$ と定数 $`\mathtt{secp256k1n}`$ の定義は[付録F](#app:signing)を参照されたい。また $`\mathbf{d}`$ を入力データとし、必要に応じてゼロを追加することで無限長に対して明確に定義する。署名が無効な場合、出力は返さない。

<span id="eq-210"></span><span id="eq-211"></span><span id="eq-212"></span><span id="eq-213"></span><span id="eq-214"></span><span id="eq-215"></span><span id="eq-216"></span><span id="eq-217"></span><span id="eq-218"></span><span id="eq-219"></span><span id="eq-220"></span><span id="eq-221"></span><span id="eq:ecrec_precompile_validity"></span>

```math
\begin{aligned}
\Xi_{\mathtt{ECREC}} &\equiv& \Xi_{\mathtt{PRE}} \quad \text{where:} & \qquad \text{(210)} \\
g_{\mathrm{r}} &=& 3000 & \qquad \text{(211)} \\
\lVert \mathbf{o} \rVert &=& \begin{cases}
  0 & \text{if} \quad v \notin \{27, 28\} \,\vee\, r = 0 \,\vee\, r \ge \mathtt{secp256k1n} \,\vee\, s = 0 \,\vee\, s \ge \mathtt{secp256k1n} \\
  0 & \text{if} \quad \mathtt{ECDSARECOVER}(h, v - 27, r, s) = \varnothing\\
  32 & \text{otherwise}
\end{cases} & \qquad \text{(212)} \\
\text{if} \quad \lVert \mathbf{o} \rVert = 32: && & \qquad \text{(213)} \\
\mathbf{o}[0..11] &=& 0 & \qquad \text{(214)} \\
\mathbf{o}[12..31] &=& \mathtt{KEC}\big(\mathtt{ECDSARECOVER}(h, v - 27, r, s)\big)[12..31] \quad \text{where:} & \qquad \text{(215)} \\
\mathbf{d}[0..(\lVert I_{\mathbf{d}} \rVert-1)] &=& I_{\mathbf{d}} & \qquad \text{(216)} \\
\mathbf{d}[\lVert I_{\mathbf{d}} \rVert..] &=& (0, 0, ...) & \qquad \text{(217)} \\
h &=& \mathbf{d}[0..31] & \qquad \text{(218)} \\
v &=& \mathbf{d}[32..63] & \qquad \text{(219)} \\
r &=& \mathbf{d}[64..95] & \qquad \text{(220)} \\
s &=& \mathbf{d}[96..127] & \qquad \text{(221)}
\end{aligned}
```

$`\Xi_{\mathtt{SHA256}}`$ と $`\Xi_{\mathtt{RIP160}}`$ を、それぞれSHA2-256およびRIPEMD-160ハッシュ関数を実装するプリコンパイル済みコントラクトとして定義する。そのgas使用量は、最も近いワード数へ切り上げた入力データ・サイズに依存する。

<span id="eq-222"></span><span id="eq-223"></span><span id="eq-224"></span><span id="eq-225"></span><span id="eq-226"></span><span id="eq-227"></span><span id="eq-228"></span>

```math
\begin{aligned}
\Xi_{\mathtt{SHA256}} &\equiv& \Xi_{\mathtt{PRE}} \quad \text{where:} & \qquad \text{(222)} \\
g_{\mathrm{r}} &=& 60 + 12\Big\lceil \dfrac{\lVert I_{\mathbf{d}} \rVert}{32} \Big\rceil & \qquad \text{(223)} \\
\mathbf{o}[0..31] &=& \mathtt{SHA256}(I_{\mathbf{d}}) & \qquad \text{(224)} \\
\Xi_{\mathtt{RIP160}} &\equiv& \Xi_{\mathtt{PRE}} \quad \text{where:} & \qquad \text{(225)} \\
g_{\mathrm{r}} &=& 600 + 120\Big\lceil \dfrac{\lVert I_{\mathbf{d}} \rVert}{32} \Big\rceil & \qquad \text{(226)} \\
\mathbf{o}[0..11] &=& 0 & \qquad \text{(227)} \\
\mathbf{o}[12..31] &=& \mathtt{RIPEMD160}(I_{\mathbf{d}}) & \qquad \text{(228)}
\end{aligned}
```

ここでは、次の形式を持つ、明確に定義されたRIPEMD-160およびSHA2-256の標準暗号関数が存在すると仮定する。

<span id="eq-229"></span><span id="eq-230"></span>

```math
\begin{aligned}
\mathtt{SHA256}(\mathbf{i} \in \mathbb{B}) & \equiv & o \in \mathbb{B}_{32} & \qquad \text{(229)} \\
\mathtt{RIPEMD160}(\mathbf{i} \in \mathbb{B}) & \equiv & o \in \mathbb{B}_{20} & \qquad \text{(230)}
\end{aligned}
```

第4のコントラクトである恒等関数 $`\Xi_{\mathtt{ID}}`$ は、出力を単に入力として定義する。

<span id="eq-231"></span><span id="eq-232"></span><span id="eq-233"></span>

```math
\begin{aligned}
\Xi_{\mathtt{ID}} &\equiv& \Xi_{\mathtt{PRE}} \quad \text{where:} & \qquad \text{(231)} \\
g_{\mathrm{r}} &=& 15 + 3\Big\lceil \dfrac{\lVert I_{\mathbf{d}} \rVert}{32} \Big\rceil & \qquad \text{(232)} \\
\mathbf{o} &=& I_{\mathbf{d}} & \qquad \text{(233)}
\end{aligned}
```

第5のコントラクトは、剰余下で任意精度の累乗を行う。ここで $`0 ^ 0`$ は1とし、すべての $`x`$ について $`x \bmod 0`$ はゼロとする。入力の第1ワードは第1の非負整数 $`B`$ が占めるバイト数を指定する。第2ワードは第2の非負整数 $`E`$ のバイト数を、第3ワードは第3の非負整数 $`M`$ のバイト数を指定する。これら三つのワードの後に $`B`$ 、 $`E`$ 、 $`M`$ が続く。入力の残りは破棄する。入力が短すぎる場合、不足するバイトはゼロとみなす。出力は $`M`$ と同じ形式へビッグエンディアンで符号化される。

<span id="eq-234"></span><span id="eq-235"></span><span id="eq-236"></span><span id="eq-237"></span><span id="eq-238"></span><span id="eq-239"></span><span id="eq-240"></span><span id="eq-241"></span><span id="eq-242"></span><span id="eq-243"></span><span id="eq-244"></span><span id="eq-245"></span><span id="eq-246"></span>

```math
\begin{aligned}
\Xi_{\mathtt{EXPMOD}} &\equiv& \Xi_{\mathtt{PRE}} \quad \text{except:} & \qquad \text{(234)} \\
g_{\mathrm{r}} &=& \max \left(200, \left\lfloor\frac{f\big(\max(\ell_{\mathrm{M}},\ell_{\mathrm{B}})\big)\max(\ell'_{\mathrm{E}},1)}{G_{\mathrm{quaddivisor}}}\right\rfloor \right) & \qquad \text{(235)} \\
G_{\mathrm{quaddivisor}} &\equiv& 3 & \qquad \text{(236)} \\
f(x) &\equiv& \left\lceil \frac{x}{8} \right\rceil ^2 & \qquad \text{(237)} \\
\ell'_{\mathrm{E}} &=& \begin{cases}
0 & \text{if}\ \ell_{\mathrm{E}}\le 32\wedge E=0 \\
\lfloor \log_2(E)\rfloor &\text{if}\ \ell_{\mathrm{E}}\le 32 \wedge E \neq 0 \\
8(\ell_{\mathrm{E}} - 32) + \lfloor \log_2(i[(96+\ell_{\mathrm{B}})..(127+\ell_{\mathrm{B}})]) \rfloor & \text{if}\ 32 < \ell_{\mathrm{E}} \wedge i[(96 + \ell_{\mathrm{B}})..(127 + \ell_{\mathrm{B}})]\neq 0 \\
8(\ell_{\mathrm{E}} - 32) & \text{otherwise} \\
\end{cases} & \qquad \text{(238)} \\
\mathbf{o} &=& \left(B^E\bmod M\right)\in\mathbb{N}_{8\ell_{\mathrm{M}}} & \qquad \text{(239)} \\
\ell_{\mathrm{B}} &\equiv& i[0..31] & \qquad \text{(240)} \\
\ell_{\mathrm{E}} &\equiv& i[32..63] & \qquad \text{(241)} \\
\ell_{\mathrm{M}} &\equiv& i[64..95] & \qquad \text{(242)} \\
B &\equiv& i[96..(95+\ell_{\mathrm{B}})] & \qquad \text{(243)} \\
E &\equiv& i[(96+\ell_{\mathrm{B}})..(95+\ell_{\mathrm{B}}+\ell_{\mathrm{E}})] & \qquad \text{(244)} \\
M &\equiv& i[(96+\ell_{\mathrm{B}}+\ell_{\mathrm{E}})..(95+\ell_{\mathrm{B}}+\ell_{\mathrm{E}}+\ell_{\mathrm{M}})] & \qquad \text{(245)} \\
i[x] &\equiv& \begin{cases}
I_{\mathbf{d}}[x] &\text{if}\ x < \lVert I_{\mathbf{d}} \rVert \\
0 &\text{otherwise}
\end{cases} & \qquad \text{(246)}
\end{aligned}
```

## E.1. zkSNARK 関連プリコンパイル済みコントラクト

いずれも素数である二つの数を選ぶ。

<span id="eq-247"></span><span id="eq-248"></span>

```math
\begin{aligned}
p &\equiv& 21888242871839275222246405745257275088696311157297823662689037894645226208583 & \qquad \text{(247)} \\
q &\equiv& 21888242871839275222246405745257275088548364400416034343698204186575808495617 & \qquad \text{(248)}
\end{aligned}
```

$`p`$ は素数であるため、 $`\{0, 1, \ldots, p - 1\}`$ は $`p`$ を法とする加算および乗算について体をなす。この体を $`F_{\mathrm{p}}`$ と呼ぶ。

集合 $`C_1`$ を次のように定義する。

<span id="eq-249"></span>

```math
C_1\equiv\{(X,Y)\in F_{\mathrm{p}}\times F_{\mathrm{p}}\mid Y^2=X^3+3\}\cup\{(0,0)\} \qquad \text{(249)}
```

相異なる要素 $`(X_1, Y_1), (X_2, Y_2)`$ について、 $`C_1`$ 上の二項演算 $`+`$ を次のように定義する。

<span id="eq-250"></span><span id="eq:ec-addition"></span>

```math
\begin{aligned}
(X_1, Y_1) + (X_2, Y_2)&\equiv&\begin{cases}
(X,Y)&\text{if}\ X_1\neq X_2\\
(0,0)&\text{otherwise}
\end{cases} & \qquad \text{(250)} \\
\lambda&\equiv&\frac{Y_2-Y_1}{X_2-X_1} \\
X&\equiv&\lambda^2-X_1-X_2 \\
Y&\equiv&\lambda(X_1-X)-Y_1
\end{aligned}
```

$`(X_1, Y_1) = (X_2, Y_2)`$ の場合、 $`C_1`$ 上の $`+`$ を次のように定義する。

<span id="eq-251"></span><span id="eq:ec-doubling"></span>

```math
\begin{aligned}
(X_1, Y_1) + (X_2, Y_2)&\equiv&\begin{cases}
(X,Y)&\text{if}\ Y_1\neq 0\\
(0,0)&\text{otherwise}
\end{cases} & \qquad \text{(251)} \\
\lambda&\equiv&\frac{3X_1^2}{2Y_1} \\
X&\equiv&\lambda^2-2X_1 \\
Y&\equiv&\lambda(X_1-X)-Y_1
\end{aligned}
```

<span id="tnref-6"></span>[訳注6](#tn-6)

$`(C_1,+)`$ は群をなすことが知られている。自然数 $`n`$ と $`C_1`$ 上の点 $`P`$ に対し、スカラー乗算 $`\cdot`$ を次のように定義する。

<span id="eq-252"></span><span id="eq:ec-scalar-multiplication"></span>

```math
n\cdot P\equiv(0,0)+\underbrace{P+\cdots+P}_{n} \qquad \text{(252)}
```

$`P_1`$ を $`C_1`$ 上の点 $`(1,2)`$ と定義する。 $`G_1`$ を $`P_1`$ が生成する $`(C_1,+)`$ の部分群とする。 $`G_1`$ は位数 $`q`$ の巡回群であることが知られている。 $`G_1`$ 内の点 $`P`$ について、 $`\log_{P_1}(P)`$ を $`n\cdot P_1=P`$ を満たす最小の自然数 $`n`$ と定義する。 $`\log_{P_1}(P)`$ は高々 $`q-1`$ である。

$`F_{p^2}`$ を体 $`F_{p}[i]/(i^2+1)`$ とする。集合 $`C_2`$ を次のように定義する。

<span id="eq-253"></span>

```math
C_2\equiv\{(X,Y)\in F_{p^2}\times F_{p^2}\mid Y^2=X^3+3(i+9)^{-1}\}\cup\{(0,0)\} \qquad \text{(253)}
```

二項演算 $`+`$ およびスカラー乗算 $`\cdot`$ を、式（[250](#eq:ec-addition)）、（[251](#eq:ec-doubling)）、（[252](#eq:ec-scalar-multiplication)）と同じ式によって定義する。 $`(C_2,+)`$ も群であることが知られている。 $`C_2`$ 内の $`P_2`$ を次のように定義する。

<span id="eq-254"></span>

```math
\begin{aligned}
P_2&\equiv&
(11559732032986387107991004021392285783925812861821192530917403151452391805634 \times i & \qquad \text{(254)} \\
&&+ 10857046999023057135944570762232829481370756359578518086990519993285655852781, \\
&& 4082367875863433681332203403145435568316851327593401208105741076214120093531 \times i \\
&&+ 8495653923123431417604973247489272438418190587263600148770280649306958101930)
\end{aligned}
```

$`G_2`$ を $`P_2`$ が生成する $`(C_2,+)`$ の部分群と定義する。 $`G_2`$ は、 $`C_2`$ 上で位数 $`q`$ を持つ唯一の巡回群であることが知られている。 $`G_2`$ 内の点 $`P`$ について、 $`\log_{P_2}(P)`$ を $`n\cdot P_2=P`$ を満たす最小の自然数 $`n`$ と定義する。この定義により、 $`\log_{P_2}(P)`$ は高々 $`q-1`$ である。

$`G_T`$ を $`F_{q^{12}}`$ の基礎となる乗法的アーベル群とする。非退化双線形写像 $`e : G_1\times G_2 \to G_T`$ が存在することが知られている。この双線形写像はタイプ3ペアリングである。このような双線形写像は複数存在するが、そのどれを $`e`$ として選んでも構わない。 $`P_T = e(P_1, P_2)`$ とし、 $`a`$ を $`G_1`$ 内の $`k`$ 個の点の集合、 $`b`$ を $`G_2`$ 内の $`k`$ 個の点の集合とする。ペアリングの定義から、次の二つは同値である。

<span id="eq-255"></span><span id="eq-256"></span><span id="eq:pairing-check"></span>

```math
\begin{aligned}
\log_{P_1}(a_1)\times\log_{P_2}(b_1)+\cdots+\log_{P_1}(a_{k})\times\log_{P_2}(b_{k})&\equiv& 1\mod q & \qquad \text{(255)} \\
\prod_{i=0}^{k}e\left(a_i, b_i\right) &=& P_T & \qquad \text{(256)}
\end{aligned}
```

したがって、ペアリング演算は式（[255](#eq:pairing-check)）を検証する方法を提供する。

<span id="tnref-7"></span>[訳注7](#tn-7)

<span id="tnref-8"></span>[訳注8](#tn-8)

32バイトの数 $`\mathbf{x}\in\mathbf{P}_{256}`$ は、 $`F_{\mathrm{p}}`$ の要素を表す場合と表さない場合がある。

<span id="eq-257"></span>

```math
\delta_{\mathrm{p}}(\mathbf{x})\equiv\begin{cases}
\mathbf{x}&\text{if}\ \mathbf{x}<p\\
\varnothing&\text{otherwise}
\end{cases} \qquad \text{(257)}
```

64バイトのデータ $`\mathbf{x}\in\mathbf{B}_{512}`$ は、 $`G_1`$ の要素を表す場合と表さない場合がある。

<span id="eq-258"></span><span id="eq-259"></span><span id="eq-260"></span><span id="eq-261"></span>

```math
\begin{aligned}
\delta_1(\mathbf{x})&\equiv&\begin{cases}
g_1&\text{if}\ g_1\in G_1\\
\varnothing&\text{otherwise}
\end{cases} & \qquad \text{(258)} \\
g_1&\equiv&\begin{cases}
(x,y)&\text{if}\ x\neq\varnothing\wedge y\neq\varnothing\\
\varnothing&\text{otherwise}
\end{cases} & \qquad \text{(259)} \\
x&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[0..31]) & \qquad \text{(260)} \\
y&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[32..63]) & \qquad \text{(261)}
\end{aligned}
```

128バイトのデータ $`\mathbf{x}\in\mathbf{B}_{1024}`$ は、 $`G_2`$ の要素を表す場合と表さない場合がある。

<span id="eq-262"></span><span id="eq-263"></span><span id="eq-264"></span><span id="eq-265"></span><span id="eq-266"></span><span id="eq-267"></span>

```math
\begin{aligned}
\delta_2(\mathbf{x})&\equiv&\begin{cases}
g_2&\text{if}\ g_2\in G_2\\
\varnothing&\text{otherwise}
\end{cases} & \qquad \text{(262)} \\
g_2&\equiv&\begin{cases}
((x_0i+y_0),(x_1i+y_1))&\text{if}\ x_0\neq\varnothing\wedge y_0\neq\varnothing\wedge x_1\neq\varnothing\wedge y_1\neq\varnothing\\
\varnothing&\text{otherwise}
\end{cases} & \qquad \text{(263)} \\
x_0&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[0..31]) & \qquad \text{(264)} \\
y_0&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[32..63]) & \qquad \text{(265)} \\
x_1&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[64..95]) & \qquad \text{(266)} \\
y_1&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[96..127]) & \qquad \text{(267)}
\end{aligned}
```

$`\Xi_{\mathtt{SNARKV}}`$ を、zkSNARK検証での使用を意図し、式（[255](#eq:pairing-check)）が成り立つかを検査するプリコンパイル済みコントラクトとして定義する。

<span id="eq-268"></span><span id="eq-269"></span><span id="eq-270"></span><span id="eq-271"></span><span id="eq-272"></span><span id="eq-273"></span><span id="eq-274"></span><span id="eq-275"></span><span id="eq-276"></span><span id="eq-277"></span><span id="eq-278"></span>

```math
\begin{aligned}
\Xi_{\mathtt{SNARKV}}&\equiv&\Xi_{\mathtt{PRE}}\quad\text{except:} & \qquad \text{(268)} \\
\qquad\Xi_{\mathtt{SNARKV}}(\boldsymbol\sigma,g,A,I)&=&\left(\varnothing,0,A,()\right)\quad\text{if}\ F & \qquad \text{(269)} \\
F&\equiv&(\lVert I_{\mathbf{d}} \rVert\bmod 192\neq 0\vee(\exists j.\ a_{\mathrm{j}}=\varnothing\vee b_{\mathrm{j}}=\varnothing)) & \qquad \text{(270)} \\
k &=& \dfrac{\lVert I_{\mathbf{d}} \rVert}{192} & \qquad \text{(271)} \\
g_{\mathrm{r}}&=& 34000k + 45000 & \qquad \text{(272)} \\
\mathbf{o}[0..31]&\equiv&\begin{cases}
0x0000000000000000000000000000000000000000000000000000000000000001&\text{if}\ v\wedge\neg F\\
0x0000000000000000000000000000000000000000000000000000000000000000&\text{if}\ \neg v\wedge\neg F
\end{cases} & \qquad \text{(273)} \\
v&\equiv&(\log_{P_1}(a_1)\times\log_{P_2}(b_1)+\cdots+\log_{P_1}(a_k)\times\log_{P_2}(b_k)\equiv 1\mod q) & \qquad \text{(274)} \\
a_1&\equiv&\delta_1(I_{\mathbf{d}}[0..63]) & \qquad \text{(275)} \\
b_1&\equiv&\delta_2(I_{\mathbf{d}}[64..191]) & \qquad \text{(276)} \\
\vdots \\
a_k&\equiv&\delta_1(I_{\mathbf{d}}[(\lVert I_{\mathbf{d}} \rVert-192)..(\lVert I_{\mathbf{d}} \rVert-129)]) & \qquad \text{(277)} \\
b_k&\equiv&\delta_2(I_{\mathbf{d}}[(\lVert I_{\mathbf{d}} \rVert-128)..(\lVert I_{\mathbf{d}} \rVert-1)]) & \qquad \text{(278)}
\end{aligned}
```

$`G_1`$ 上の加算を行うプリコンパイル済みコントラクトを定義する。

<span id="eq-279"></span><span id="eq-280"></span><span id="eq-281"></span><span id="eq-282"></span><span id="eq-283"></span><span id="eq-284"></span><span id="eq-285"></span><span id="eq:complemented_input"></span>

```math
\begin{aligned}
\Xi_{\mathtt{BN\_ADD}}&\equiv&\Xi_{\mathtt{BN\_PRE}}\quad\text{except:} & \qquad \text{(279)} \\
\Xi_{\mathtt{BN\_ADD}}(\boldsymbol\sigma,g,A,I)&=&\left(\varnothing,0,A,()\right)\quad\text{if}\ x=\varnothing\vee y=\varnothing & \qquad \text{(280)} \\
g_{\mathrm{r}} &=& 150 & \qquad \text{(281)} \\
\mathbf{o}&\equiv&\delta_1^{-1}(x+y)\quad\text{ここで }+\text{ は }G_1\text{ の群演算} & \qquad \text{(282)} \\
x&\equiv&\delta_1\left(\bar I_{\mathbf{d}}[0..63]\right) & \qquad \text{(283)} \\
y&\equiv&\delta_1\left(\bar I_{\mathbf{d}}[64..127]\right) & \qquad \text{(284)} \\
\bar I_{\mathbf{d}}[x]&\equiv&\begin{cases}
I_{\mathbf{d}}[x]&\text{if}\ x < \lVert I_{\mathbf{d}} \rVert\\
0&\text{otherwise}
\end{cases} & \qquad \text{(285)}
\end{aligned}
```

<span id="tnref-9"></span>[訳注9](#tn-9)

$`G_1`$ 上のスカラー乗算を行うプリコンパイル済みコントラクトを定義する。ここで $`\bar I_{\mathbf{d}}`$ は式（[285](#eq:complemented_input)）で定義される。

<span id="eq-286"></span><span id="eq-287"></span><span id="eq-288"></span><span id="eq-289"></span><span id="eq-290"></span><span id="eq-291"></span>

```math
\begin{aligned}
\Xi_{\mathtt{BN\_MUL}}&\equiv&\Xi_{\mathtt{PRE}}\quad\text{except:} & \qquad \text{(286)} \\
\Xi_{\mathtt{BN\_MUL}}(\boldsymbol\sigma,g,A,I)&=&\left(\varnothing,0,A,()\right)\quad\text{if}\ x=\varnothing & \qquad \text{(287)} \\
g_{\mathrm{r}} &=& 6000 & \qquad \text{(288)} \\
\mathbf{o}&\equiv&\delta_1^{-1}(n\cdot x)\quad\text{ここで }\cdot\text{ は }G_1\text{ のスカラー乗算} & \qquad \text{(289)} \\
x&\equiv&\delta_1\left(\bar I_{\mathbf{d}}[0..63]\right) & \qquad \text{(290)} \\
n&\equiv&\bar I_{\mathbf{d}}[64..95] & \qquad \text{(291)}
\end{aligned}
```

## E.2. BLAKE2 プリコンパイル済みコントラクト

[(Hess et al. 2016)](#ref-EIP-152) によるEIP-152は、BLAKE2暗号学的ハッシュ・アルゴリズムで用いる圧縮関数 $`\mathtt{F}`$ を実装するプリコンパイル済みコントラクトとして $`\Xi_{\mathtt{BLAKE2\_F}}`$ を定義する。圧縮関数 $`\mathtt{F}`$ は、[(Saarinen and Aumasson 2015)](#ref-RFC-7693) によるRFC 7693で規定されている。

<span id="eq-292"></span><span id="eq-293"></span><span id="eq-294"></span><span id="eq-295"></span><span id="eq-296"></span><span id="eq-297"></span><span id="eq-298"></span><span id="eq-299"></span><span id="eq-300"></span><span id="eq-301"></span><span id="eq-302"></span><span id="eq-303"></span><span id="eq-304"></span><span id="eq-305"></span><span id="eq-306"></span>

```math
\begin{aligned}
\Xi_{\mathtt{BLAKE2\_F}}&\equiv&\Xi_{\mathtt{PRE}}\quad\text{except:} & \qquad \text{(292)} \\
\Xi_{\mathtt{BLAKE2\_F}}(\boldsymbol\sigma,g,A,I)&=&\left(\varnothing,0,A,()\right)\quad\text{if}\ \lVert I_{\mathbf{d}}\rVert \neq 213 \vee f \notin \{0, 1\} & \qquad \text{(293)} \\
g_{\mathrm{r}} &=& r & \qquad \text{(294)} \\
\mathbf{o} &\equiv& \mathtt{LE}_8(h'_0)\cdot ... \cdot \mathtt{LE}_8(h'_7) & \qquad \text{(295)} \\
(h'_0,\dots,h'_7) &\equiv& \mathtt{F}(h, m, t_\mathrm{low}, t_\mathrm{high}, f) \quad(r\text{ ラウンド、}w = 64) & \qquad \text{(296)} \\
\mathtt{BE}_4(r) &\equiv& I_{\mathbf{d}}[0..4] & \qquad \text{(297)} \\
\mathtt{LE}_8(h_0) &\equiv& I_{\mathbf{d}}[4..12] & \qquad \text{(298)} \\
&\dots& & \qquad \text{(299)} \\
\mathtt{LE}_8(h_7) &\equiv& I_{\mathbf{d}}[60..68] & \qquad \text{(300)} \\
\mathtt{LE}_8(m_0) &\equiv& I_{\mathbf{d}}[68..76] & \qquad \text{(301)} \\
&\dots& & \qquad \text{(302)} \\
\mathtt{LE}_8(m_{15}) &\equiv& I_{\mathbf{d}}[188..196] & \qquad \text{(303)} \\
\mathtt{LE}_8(t_\mathrm{low}) &\equiv& I_{\mathbf{d}}[196..204] & \qquad \text{(304)} \\
\mathtt{LE}_8(t_\mathrm{high}) &\equiv& I_{\mathbf{d}}[204..212] & \qquad \text{(305)} \\
f &\equiv& I_{\mathbf{d}}[212] & \qquad \text{(306)}
\end{aligned}
```

ここで $`r \in \mathbb{B}_{32}`$ 、 $`\forall i \in 0..7: h_i \in \mathbb{B}_{64}`$ 、 $`\forall i \in 0..15: m_i \in \mathbb{B}_{64}`$ 、 $`t_\mathrm{low} \in \mathbb{B}_{64}`$ 、 $`t_\mathrm{high} \in \mathbb{B}_{64}`$ 、 $`f \in \mathbb{B}_8`$ である。 $`\mathtt{BE}_k`$ は $`k`$ バイトのビッグエンディアン表現である（[195](#eq:BE)と比較されたい）。

<span id="tnref-10"></span>[訳注10](#tn-10)

<span id="eq-307"></span>

```math
\mathtt{BE}_k(x) \equiv (b_0, b_1, ..., b_{k-1}): x = \sum_{n = 0}^{k-1} b_n \cdot 256^{k-1-n} \qquad \text{(307)}
```

また、 $`\mathtt{LE}_k`$ は $`k`$ バイトのリトルエンディアン表現である。

<span id="eq-308"></span>

```math
\mathtt{LE}_k(x) \equiv (b_0, b_1, ..., b_{k-1}): x = \sum_{n = 0}^{k-1} b_n \cdot 256^n \qquad \text{(308)}
```

<span id="app:signing"></span>

# 付録F. トランザクションへの署名

トランザクションは、公開鍵を復元可能なECDSA署名を用いて署名される。この方式は [(Courtois, Grajek, and Naik 2014)](#ref-Courtois2014) が記述するSECP-256k1曲線を使用し、[(Gura et al. 2004)](#ref-gura2004comparing) の全15ページ中9ページ、第3段落に記述された方法と同様に実装される。

送信者は妥当な秘密鍵 $`p_{\mathrm{r}}`$ を持つと仮定する。これは範囲 $`[1, \mathtt{secp256k1n} - 1]`$ から無作為に選ばれた正整数であり、ビッグエンディアン形式の長さ32のバイト配列として表される。

関数 $`\mathtt{ECDSAPUBKEY}`$ 、 $`\mathtt{ECDSASIGN}`$ 、 $`\mathtt{ECDSARECOVER}`$ が存在すると仮定する。これらは、たとえば[(Johnson, Menezes, and Vanstone 2001)](#ref-ECDSAcerticom)などの文献で形式的に定義されている。

<span id="eq-309"></span><span id="eq-310"></span><span id="eq-311"></span>

```math
\begin{aligned}
\mathtt{ECDSAPUBKEY}(p_{\mathrm{r}} \in \mathbb{B}_{32}) & \equiv & p_{\mathrm{u}} \in \mathbb{B}_{64} & \qquad \text{(309)} \\
\mathtt{ECDSASIGN}(e \in \mathbb{B}_{32}, p_{\mathrm{r}} \in \mathbb{B}_{32}) & \equiv & (v \in \mathbb{B}_{1}, r \in \mathbb{B}_{32}, s \in \mathbb{B}_{32}) & \qquad \text{(310)} \\
\mathtt{ECDSARECOVER}(e \in \mathbb{B}_{32}, v \in \mathbb{B}_{1}, r \in \mathbb{B}_{32}, s \in \mathbb{B}_{32}) & \equiv & p_{\mathrm{u}} \in \mathbb{B}_{64} & \qquad \text{(311)}
\end{aligned}
```

ここで $`p_{\mathrm{u}}`$ は公開鍵であり、それぞれ $`2^{256}`$ 未満である二つの正整数を連結して構成した64バイトのバイト配列と仮定する。 $`p_{\mathrm{r}}`$ は秘密鍵であり、32バイトのバイト配列（または前述の範囲内の単一の正整数）である。また $`e`$ はトランザクションのハッシュ [$`h(T)`$](#h_of_T) である。<span id="v"></span> $`v`$ は「復元識別子（recovery identifier）」と仮定する。復元識別子は、 $`r`$ がx座標となる曲線上の点について、その座標の偶奇性と有限性を指定する1バイト値である。この値の範囲は $`[0, 3]`$ だが、無限値を表す上位二つの可能性は無効と定める。値0は偶数の $`y`$ 値を、値1は奇数の $`y`$ 値を表す。

次の条件がすべて真でない限り、ECDSA署名は無効であると定める。

<span id="eq-312"></span><span id="eq-313"></span><span id="eq-314"></span>

```math
\begin{aligned}
0 < {r} &< \mathtt{secp256k1n} & \qquad \text{(312)} \\
0 < {s} &< \mathtt{secp256k1n} \div 2 + 1 & \qquad \text{(313)} \\
v &\in \{0,1\} & \qquad \text{(314)}
\end{aligned}
```

ここで、

<span id="eq-315"></span>

```math
\begin{aligned}
\mathtt{secp256k1n} &= 115792089237316195423570985008687907852837564279074904382605163141518161494337 & \qquad \text{(315)}
\end{aligned}
```

$`s`$ に対するこの制限は、 $`\Xi_{\mathtt{ECREC}}`$ プリコンパイルの制限 [212](#eq:ecrec_precompile_validity) より厳しいことに注意されたい。詳細は [(Buterin 2015)](#ref-EIP-2) によるEIP-2を参照されたい。

所与の秘密鍵 $`p_{\mathrm{r}}`$ に対応するEthereumアドレス $`A(p_{\mathrm{r}})`$ （160ビット値）は、対応するECDSA公開鍵のKeccak-256ハッシュの右端160ビットとして定義される。

<span id="eq-316"></span>

```math
A(p_{\mathrm{r}}) = \mathcal{B}_{96..255}\big(\mathtt{KEC}\big( \mathtt{ECDSAPUBKEY}(p_{\mathrm{r}}) \big) \big) \qquad \text{(316)}
```

<div id="h_of_T">

</div>

署名対象のメッセージ・ハッシュ $`h(T)`$ は、トランザクションのKeccak-256ハッシュである。四種類の署名方式が利用できる。

<span id="eq-317"></span><span id="eq-318"></span>

```math
\begin{aligned}
L_{\mathrm{X}}(T) & \equiv & \begin{cases}
(T_{\mathrm{n}}, T_{\mathrm{p}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}) & \text{if} \; T_{\mathrm{x}} = 0 \land T_{\mathrm{w}} \in \{27, 28\} \\
(T_{\mathrm{n}}, T_{\mathrm{p}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, \beta, (), ()) & \text{if} \; T_{\mathrm{x}} = 0 \land T_{\mathrm{w}} \in \{2\beta + 35, 2\beta + 36\} \\
(T_{\mathrm{c}}, T_{\mathrm{n}}, T_{\mathrm{p}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, T_{\mathbf{A}}) & \text{if} \; T_{\mathrm{x}} = 1 \\
(T_{\mathrm{c}}, T_{\mathrm{n}}, T_{\mathrm{f}}, T_{\mathrm{m}},  T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, T_{\mathbf{A}}) & \text{if} \; T_{\mathrm{x}} = 2
\end{cases} & \qquad \text{(317)} \\
\text{where} \\
\mathbf{p} & \equiv & \begin{cases}
T_{\mathbf{i}} & \text{if}\ T_{\mathrm{t}} = \varnothing \\
T_{\mathbf{d}} & \text{otherwise}
\end{cases} \\
h(T) & \equiv & \begin{cases}
\mathtt{KEC}( \mathtt{RLP}(L_{\mathrm{X}}(T)) ) & \text{if} \; T_{\mathrm{x}} = 0 \\
\mathtt{KEC}( T_{\mathrm{x}} \cdot \mathtt{RLP}(L_{\mathrm{X}}(T)) ) & \text{otherwise}
\end{cases} & \qquad \text{(318)}
\end{aligned}
```

署名済みトランザクション $`G(T, p_{\mathrm{r}})`$ を次のように定義する。

<span id="eq-319"></span><span id="eq-320"></span>

```math
\begin{aligned}
G(T, p_{\mathrm{r}}) \equiv T \quad \text{except:} & \qquad \text{(319)} \\
(T_{\mathrm{y}}, T_{\mathrm{r}}, T_{\mathrm{s}}) = \mathtt{ECDSASIGN}(h(T), p_{\mathrm{r}}) & \qquad \text{(320)}
\end{aligned}
```

[前述の内容を繰り返すと](#T__r_T__s)、

<span id="eq-321"></span><span id="eq-322"></span>

```math
\begin{aligned}
{T_{\mathrm{r}}} = r & \qquad \text{(321)} \\
{T_{\mathrm{s}}} = s & \qquad \text{(322)}
\end{aligned}
```

であり、レガシー・トランザクションの $`T_{\mathrm{w}}`$ は $`27 + T_{\mathrm{y}}`$ または $`2\beta + 35 + T_{\mathrm{y}}`$ のいずれかである。

これにより、トランザクションの送信者関数 $`S`$ を次のように定義できる。

<span id="eq-323"></span><span id="eq-324"></span>

```math
\begin{aligned}
S(T) &\equiv& \mathcal{B}_{96..255}\big(\mathtt{KEC}\big( \mathtt{ECDSARECOVER}(h(T), v, T_{\mathrm{r}}, T_{\mathrm{s}}) \big) \big) & \qquad \text{(323)} \\
v &\equiv& \begin{cases}
T_{\mathrm{w}} - 27 & \text{if} \; T_{\mathrm{x}} = 0 \land T_{\mathrm{w}} \in \{27, 28\} \\
(T_{\mathrm{w}}-35) \bmod 2 & \text{if} \ T_{\mathrm{x}} = 0 \land T_{\mathrm{w}} \in \{2\beta + 35, 2\beta + 36\} \\
T_{\mathrm{y}} & \text{if} \ T_{\mathrm{x}} = 1 \lor T_{\mathrm{x}} = 2
\end{cases} & \qquad \text{(324)}
\end{aligned}
```

署名済みトランザクションの送信者が署名者のアドレスに等しいという主張は自明であろう。

<span id="eq-325"></span>

```math
\forall T: \forall p_{\mathrm{r}}: S(G(T, p_{\mathrm{r}})) \equiv A(p_{\mathrm{r}}) \qquad \text{(325)}
```

<span id="app:fees"></span>

# 付録G. 手数料表

手数料表 $`G`$ は、トランザクションが引き起こし得る複数の抽象演算について、gas単位の相対コストに対応するスカラー値のタプルである。

| 名前 | 値 | 説明 |
| --- | --- | --- |
| $`G_{\mathrm{zero}}`$ | 0 | 集合 $`W_{\mathrm{zero}}`$ の演算には支払わない。 |
| $`G_{\mathrm{jumpdest}}`$ | 1 | JUMPDEST演算に支払うgas量。 |
| $`G_{\mathrm{base}}`$ | 2 | 集合 $`W_{\mathrm{base}}`$ の演算に支払うgas量。 |
| $`G_{\mathrm{verylow}}`$ | 3 | 集合 $`W_{\mathrm{verylow}}`$ の演算に支払うgas量。 |
| $`G_{\mathrm{low}}`$ | 5 | 集合 $`W_{\mathrm{low}}`$ の演算に支払うgas量。 |
| $`G_{\mathrm{mid}}`$ | 8 | 集合 $`W_{\mathrm{mid}}`$ の演算に支払うgas量。 |
| $`G_{\mathrm{high}}`$ | 10 | 集合 $`W_{\mathrm{high}}`$ の演算に支払うgas量。 |
| $`G_{\mathrm{warmaccess}}`$ | 100 | ウォームなアカウントまたはストレージへのアクセス・コスト。 |
| $`G_{\mathrm{accesslistaddress}}`$ | 2400 | アクセス・リストによってアカウントをウォームにするコスト。 |
| $`G_{\mathrm{accessliststorage}}`$ | 1900 | アクセス・リストによってストレージをウォームにするコスト。 |
| $`G_{\mathrm{coldaccountaccess}}`$ | 2600 | コールドなアカウントへのアクセス・コスト。 |
| $`G_{\mathrm{coldsload}}`$ | 2100 | コールドなストレージへのアクセス・コスト。 |
| $`G_{\mathrm{sset}}`$ | 20000 | SSTORE演算によってストレージ値をゼロから非ゼロへ設定するときに支払う。 |
| $`G_{\mathrm{sreset}}`$ | 2900 | SSTORE演算によってストレージ値のゼロ／非ゼロの別が変わらないとき、または ゼロに設定するときに支払う。 |
| $`R_{\mathrm{sclear}}`$ | 4800 | ストレージ値を非ゼロからゼロへ設定するときに与える還付（還付カウンタへ加算）。 還付額は $`G_{\mathrm{sreset}} + G_{\mathrm{accessliststorage}}`$ と定義される。 |
| $`G_{\mathrm{selfdestruct}}`$ | 5000 | SELFDESTRUCT演算に支払うgas量。 |
| $`G_{\mathrm{create}}`$ | 32000 | CREATE演算に支払う。 |
| $`G_{\mathrm{codedeposit}}`$ | 200 | CREATE演算がコードを状態へ正常に配置する際に、1バイトごとに支払う。 |
| $`G_{\mathrm{initcodeword}}`$ | 2 | デプロイ・トランザクション、CREATE演算、またはCREATE2演算の開始時に、 初期化コード1ワードごとに支払う。 |
| $`G_{\mathrm{callvalue}}`$ | 9000 | CALL演算の一部として非ゼロ値を移転するときに支払う。 |
| $`G_{\mathrm{callstipend}}`$ | 2300 | 非ゼロ値の移転について $`G_{\mathrm{callvalue}}`$ から差し引き、呼出先コントラクトへ与える給付gas。 |
| $`G_{\mathrm{newaccount}}`$ | 25000 | アカウントを作成するCALLまたはSELFDESTRUCT演算に支払う。 |
| $`G_{\mathrm{exp}}`$ | 10 | EXP演算に対する部分的な支払い。 |
| $`G_{\mathrm{expbyte}}`$ | 50 | EXP演算について、指数のバイト数を乗じる部分的な支払い。 |
| $`G_{\mathrm{memory}}`$ | 3 | メモリ拡張時、追加する1ワードごとに支払う。 |
| $`G_\text{txcreate}`$ | 32000 | *Homestead* 移行後、コントラクトを作成するすべてのトランザクションが支払う。 |
| $`G_{\mathrm{txdatazero}}`$ | 4 | トランザクションのデータまたはコードに含まれるゼロ・バイトごとに支払う。 |
| $`G_{\mathrm{txdatanonzero}}`$ | 16 | トランザクションのデータまたはコードに含まれる非ゼロ・バイトごとに支払う。 |
| $`G_{\mathrm{transaction}}`$ | 21000 | トランザクションごとに支払う。 |
| $`G_{\mathrm{log}}`$ | 375 | LOG演算に対する部分的な支払い。 |
| $`G_{\mathrm{logdata}}`$ | 8 | LOG演算のデータ1バイトごとに支払う。 |
| $`G_{\mathrm{logtopic}}`$ | 375 | LOG演算のトピックごとに支払う。 |
| $`G_{\mathrm{keccak256}}`$ | 30 | KECCAK256演算ごとに支払う。 |
| $`G_{\mathrm{keccak256word}}`$ | 6 | KECCAK256演算の入力データについて、切り上げたワードごとに支払う。 |
| $`G_{\mathrm{copy}}`$ | 3 | \*COPY演算に対する部分的な支払いであり、コピーするワード数を切り上げた値を乗じる。 |
| $`G_{\mathrm{blockhash}}`$ | 20 | BLOCKHASH演算ごとの支払い。 |

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

[第9節](#ch:model)で先に規定したとおり、これらの定義は同節の最終的な文脈で行われる。特に、 $`O`$ をEVM状態進行関数と仮定し、次サイクルの状態 $`(\boldsymbol{\sigma}', \boldsymbol{\mu}')`$ に関する項を次のように定義する。

<span id="eq-332"></span>

```math
O(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \equiv (\boldsymbol{\sigma}', \boldsymbol{\mu}', A', I) \quad \text{ただし、後述の例外を除く} \qquad \text{(332)}
```

ここでは、[第9節](#ch:model)の状態遷移規則に対する命令ごとの各種例外と、命令固有の $`J`$ および $`C`$ の追加定義を示す。また各命令について、同節で定義した、スタックへ追加する項目数 $`\alpha`$ とスタックから取り除く項目数 $`\delta`$ も示す。

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
| 0x3a | GASPRICE | 0 | 1 | 現在の環境のgas価格を取得する。 これは[第6節](#ch:transactions)で定義した*実効gas価格*である。 *London* ハードフォーク以降、この値はバリデータが受け取る額ではなく、単に送信者が支払う額を表すことに注意されたい。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv I_{\mathrm{p}}`$ |
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
| 0x46 | CHAINID | 0 | 1 | [チェーンID](#chain_id)を取得する。 $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv \beta`$ |
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
| 0x56 | JUMP | 1 | 0 | プログラム・カウンタを変更する。 $`J_{\text{JUMP}}(\boldsymbol{\mu}) \equiv \boldsymbol{\mu}_{\mathbf{s}}[0]`$ これは当該値を $`\boldsymbol{\mu}_{\mathrm{pc}}`$ へ書き込む効果を持つ。[第9節](#ch:model)を参照されたい。 |
| 0x57 | JUMPI | 2 | 0 | 条件付きでプログラム・カウンタを変更する。 $`J_{\text{JUMPI}}(\boldsymbol{\mu}) \equiv \begin{cases} \boldsymbol{\mu}_{\mathbf{s}}[0] & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[1] \neq 0 \\ \boldsymbol{\mu}_{\mathrm{pc}} + 1 & \text{otherwise} \end{cases}`$ これは当該値を $`\boldsymbol{\mu}_{\mathrm{pc}}`$ へ書き込む効果を持つ。[第9節](#ch:model)を参照されたい。 |
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
| 0xf0 | CREATE | 3 | 1 | 関連コードを持つ新しいアカウントを作成する。 $`\mathbf{i} \equiv \boldsymbol{\mu}_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[1] \dots (\boldsymbol{\mu}_{\mathbf{s}}[1] + \boldsymbol{\mu}_{\mathbf{s}}[2] - 1) ]`$ $`\zeta \equiv \varnothing`$ $`(\boldsymbol{\sigma}', g', A', z, \mathbf{o}) \equiv \begin{cases} \Lambda(\boldsymbol{\sigma}^{*}, A, I_{\mathrm{a}}, I_{\mathrm{o}}, L(\boldsymbol{\mu}_{\mathrm{g}}), I_{\mathrm{p}}, \boldsymbol{\mu}_{\mathbf{s}}[0], \mathbf{i}, I_{\mathrm{e}} + 1, \zeta, I_{\mathrm{w}}) & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[0] \leqslant \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}} \; \wedge \\ \quad &\; I_{\mathrm{e}} < 1024 \wedge \lVert \mathbf{i} \rVert \leqslant 49152\\ \big(\boldsymbol{\sigma}, L(\boldsymbol{\mu}_{\mathrm{g}}), A, 0, () \big) & \text{otherwise} \end{cases}`$ $`\boldsymbol{\sigma}^{*} \equiv \boldsymbol{\sigma} \quad \text{except} \quad \boldsymbol{\sigma}^{*}[I_{\mathrm{a}}]_{\mathrm{n}} = \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{n}} + 1`$ $`\boldsymbol{\mu}'_{\mathrm{g}} \equiv \boldsymbol{\mu}_{\mathrm{g}} - L(\boldsymbol{\mu}_{\mathrm{g}}) + g'`$ $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv x`$ $`z = 0`$ 、すなわち[コントラクト作成処理が失敗](#contract_creation_result)した場合、 または $`\lVert \mathbf{i} \rVert > 49152`$ （初期化コードが49152バイトより長い）、 または $`I_{\mathrm{e}} = 1024`$ （最大呼出し深度の上限に達した）、 または $`\boldsymbol{\mu}_{\mathbf{s}}[0] > \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}}`$ （呼出元の残高が値の移転を満たすには不足している）ならば $`x=0`$ とする。 それ以外では、 $`x=\mathtt{ADDR}(I_{\mathrm{a}}, \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{n}}, \zeta, \mathbf{i} )`$ 、すなわち新たに作成したアカウントのアドレス（[95](#eq:new-address)）とする。 $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[1], \boldsymbol{\mu}_{\mathbf{s}}[2])`$ $`\boldsymbol{\mu}'_{\mathbf{o}} \equiv \begin{cases} () & \text{if} \quad z = 1 \\ \mathbf{o} & \text{otherwise} \end{cases}`$ したがってオペランドの順序は、値、入力オフセット、入力サイズである。 |
| 0xf1 | CALL | 7 | 1 | アカウントへメッセージ呼出しを行う。 $`\mathbf{i} \equiv \boldsymbol{\mu}_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[3] \dots (\boldsymbol{\mu}_{\mathbf{s}}[3] + \boldsymbol{\mu}_{\mathbf{s}}[4] - 1) ]`$ $`(\boldsymbol{\sigma}', g', A', x, \mathbf{o}) \equiv \begin{cases} \begin{array}{l}\Theta(\boldsymbol{\sigma}, A^{*}, I_{\mathrm{a}}, I_{\mathrm{o}}, t, t, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A),\\ \quad I_{\mathrm{p}}, \boldsymbol{\mu}_{\mathbf{s}}[2], \boldsymbol{\mu}_{\mathbf{s}}[2], \mathbf{i}, I_{\mathrm{e}} + 1, I_{\mathrm{w}})\end{array} & \begin{array}{l}\text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[2] \leqslant \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}} \;\wedge \\ \quad\quad I_{\mathrm{e}} < 1024\end{array}\\ (\boldsymbol{\sigma}, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A), A^{*}, 0, ()) & \text{otherwise} \end{cases}`$ $`n \equiv \min(\{ \boldsymbol{\mu}_{\mathbf{s}}[6], \lVert \mathbf{o} \rVert\})`$ $`\boldsymbol{\mu}'_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[5] \dots (\boldsymbol{\mu}_{\mathbf{s}}[5] + n - 1) ] = \mathbf{o}[0 \dots (n - 1)]`$ $`\boldsymbol{\mu}'_{\mathbf{o}} = \mathbf{o}`$ $`\boldsymbol{\mu}'_{\mathrm{g}} \equiv \boldsymbol{\mu}_{\mathrm{g}} - C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A) + g'`$ $`\boldsymbol{\mu}'_{\mathbf{s}}[0] \equiv x`$ $`A^{*} \equiv A \quad \text{except} \quad A^{*}_{\mathbf{a}} \equiv A_{\mathbf{a}} \cup \{t\}`$ $`t \equiv \boldsymbol{\mu}_{\mathbf{s}}[1] \bmod 2^{160}`$ $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[3], \boldsymbol{\mu}_{\mathbf{s}}[4]), \boldsymbol{\mu}_{\mathbf{s}}[5], \boldsymbol{\mu}_{\mathbf{s}}[6])`$ [この演算のコード実行が失敗](#code_execution_result)した場合、または $`\boldsymbol{\mu}_{\mathbf{s}}[2] > \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}}`$ （資金不足）、または $`I_{\mathrm{e}} = 1024`$ （呼出し深度の上限に到達）の場合は $`x=0`$ とし、 それ以外では $`x=1`$ とする。 したがってオペランドの順序は、gas、宛先、値、入力オフセット、入力サイズ、出力オフセット、出力サイズである。 $`C_{\text{CALL}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) \equiv C_{\text{GASCAP}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) + C_{\text{EXTRA}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A)`$ $`C_{\text{CALLGAS}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) \equiv \begin{cases} C_{\text{GASCAP}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) + G_{\mathrm{callstipend}} & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[2] \neq 0 \\ C_{\text{GASCAP}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) & \text{otherwise} \end{cases}`$ $`C_{\text{GASCAP}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) \equiv \begin{cases} \min\{ L(\boldsymbol{\mu}_{\mathrm{g}} - C_{\text{EXTRA}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A)), \boldsymbol{\mu}_{\mathbf{s}}[0] \} & \text{if} \quad \boldsymbol{\mu}_{\mathrm{g}} \ge C_{\text{EXTRA}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A)\\ \boldsymbol{\mu}_{\mathbf{s}}[0] & \text{otherwise} \end{cases}`$ $`C_{\text{EXTRA}}(\boldsymbol{\sigma}, \boldsymbol{\mu}, A) \equiv C_{\mathrm{aaccess}}(t, A) + C_{\text{XFER}}(\boldsymbol{\mu}) + C_{\text{NEW}}(\boldsymbol{\sigma}, \boldsymbol{\mu})`$ $`C_{\text{XFER}}(\boldsymbol{\mu}) \equiv \begin{cases} G_{\mathrm{callvalue}} & \text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[2] \neq 0 \\ 0 & \text{otherwise} \end{cases}`$ $`C_{\text{NEW}}(\boldsymbol{\sigma}, \boldsymbol{\mu}) \equiv \begin{cases} G_{\mathrm{newaccount}} & \text{if} \quad \mathtt{DEAD}(\boldsymbol{\sigma}, t) \wedge \boldsymbol{\mu}_{\mathbf{s}}[2] \neq 0 \\ 0 & \text{otherwise} \end{cases}`$ |
| 0xf2 | CALLCODE | 7 | 1 | 別のアカウントのコードを用いて、このアカウントへメッセージ呼出しを行う。 次の点を除き、CALLと厳密に等価である。 $`(\boldsymbol{\sigma}', g', A', x, \mathbf{o}) \equiv \begin{cases}\begin{array}{l}\Theta(\boldsymbol{\sigma}, A^{*}, I_{\mathrm{a}}, I_{\mathrm{o}}, I_{\mathrm{a}}, t, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A), \\ \quad I_{\mathrm{p}}, \boldsymbol{\mu}_{\mathbf{s}}[2], \boldsymbol{\mu}_{\mathbf{s}}[2], \mathbf{i}, I_{\mathrm{e}} + 1, I_{\mathrm{w}})\end{array} & \begin{array}{l}\text{if} \quad \boldsymbol{\mu}_{\mathbf{s}}[2] \leqslant \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}} \;\wedge\\ \quad\quad{}I_{\mathrm{e}} < 1024\end{array} \\ (\boldsymbol{\sigma}, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A), A^{*}, 0, ()) & \text{otherwise} \end{cases}`$ 呼出し $`\Theta`$ の第4引数が、（CALLの場合の）スタック第2値 $`\boldsymbol{\mu}_{\mathbf{s}}[1]`$ から現在のアドレス $`I_{\mathrm{a}}`$ へ変更されていることに注意されたい。これは、受信者が実際には現在と同じアカウントであり、コードだけが置き換えられることを意味する。 |
| 0xf3 | <span id="RETURN"></span>RETURN | 2 | 0 | 出力データを返して実行を停止する。 $`H_{\text{RETURN}}(\boldsymbol{\mu}) \equiv \boldsymbol{\mu}_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[0] \dots ( \boldsymbol{\mu}_{\mathbf{s}}[0] + \boldsymbol{\mu}_{\mathbf{s}}[1] - 1 ) ]`$ これは、出力を定義したうえで、この地点で実行を停止する効果を持つ。 [第9節](#ch:model)を参照されたい。 $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[0], \boldsymbol{\mu}_{\mathbf{s}}[1])`$ |

| 値 | ニーモニック | $`\delta`$ | $`\alpha`$ | 説明 |
| --- | --- | --- | --- | --- |
| 0xf4 | DELEGATECALL | 6 | 1 | 現在の*送信者*と*値*を維持しつつ、別のアカウントのコードを用いて、このアカウントへメッセージ呼出しを行う。 CALLと比べ、DELEGATECALLは引数が一つ少ない。省略する引数は $`\boldsymbol{\mu}_{\mathbf{s}}[2]`$ である。そのため、CALLの定義にある $`\boldsymbol{\mu}_{\mathbf{s}}[3]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[4]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[5]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[6]`$ は、それぞれ $`\boldsymbol{\mu}_{\mathbf{s}}[2]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[3]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[4]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[5]`$ に置き換える。それ以外では、次の点を除きCALLと等価である。 $`(\boldsymbol{\sigma}', g', A', x, \mathbf{o}) \equiv \begin{cases}\begin{array}{l}\Theta(\boldsymbol{\sigma}, A^{*}, I_{\mathrm{s}}, I_{\mathrm{o}}, I_{\mathrm{a}}, t, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A), \\\quad I_{\mathrm{p}}, 0, I_{\mathrm{v}}, \mathbf{i}, I_{\mathrm{e}} + 1, I_{\mathrm{w}})\end{array} & \text{if} \quad I_{\mathrm{e}} < 1024 \\ (\boldsymbol{\sigma}, C_{\text{CALLGAS}}(\boldsymbol{\sigma},\boldsymbol{\mu},A), A^{*}, 0, ()) & \text{otherwise} \end{cases}`$ 呼出し $`\Theta`$ の第4引数に加え、第2引数および第9引数も変更されていることに注意されたい。 これは、受信者が実際には現在と同じアカウントであり、コードだけが置き換えられ、かつ文脈がほぼ完全に同一であることを意味する。 |
| 0xf5 | <span id="create2"></span>CREATE2 | 4 | 1 | 関連コードを持つ新しいアカウントを作成する。 次の点を除き、CREATEと厳密に等価である。 saltは $`\zeta \equiv \boldsymbol{\mu}_{\mathbf{s}}[3]`$ である。 |
| 0xfa | STATICCALL | 6 | 1 | アカウントへ静的メッセージ呼出しを行う。 次の点を除き、CALLと厳密に等価である。 引数 $`\boldsymbol{\mu}_{\mathbf{s}}[2]`$ を $`0`$ に置き換える。 後続の引数 $`\boldsymbol{\mu}_{\mathbf{s}}[3]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[4]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[5]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[6]`$ は、それぞれ $`\boldsymbol{\mu}_{\mathbf{s}}[2]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[3]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[4]`$ 、 $`\boldsymbol{\mu}_{\mathbf{s}}[5]`$ に置き換える。 $`\Theta`$ の最後の引数は $`\bot`$ である。 |
| 0xfd | <span id="REVERT"></span>REVERT | 2 | 0 | 状態変更をリバートしつつ、データと残存gasを返して実行を停止する。 $`H_{\text{RETURN}}(\boldsymbol{\mu}) \equiv \boldsymbol{\mu}_{\mathbf{m}}[ \boldsymbol{\mu}_{\mathbf{s}}[0] \dots ( \boldsymbol{\mu}_{\mathbf{s}}[0] + \boldsymbol{\mu}_{\mathbf{s}}[1] - 1 ) ]`$ この演算の効果は（[152](#eq:X-def)）で記述する。 gasの計算にはメモリ拡張関数を用いる。 $`\boldsymbol{\mu}'_{\mathrm{i}} \equiv M(\boldsymbol{\mu}_{\mathrm{i}}, \boldsymbol{\mu}_{\mathbf{s}}[0], \boldsymbol{\mu}_{\mathbf{s}}[1])`$ |
| 0xfe | INVALID | $`\varnothing`$ | $`\varnothing`$ | 無効と指定された命令。 |
| 0xff | SELFDESTRUCT | 1 | 0 | 実行を停止し、後で削除するアカウントとして登録する。*Shanghai* 更新以降、このオペコードは非推奨とされていることに注意されたい。 今後の更新で、その振る舞いに破壊的変更が加えられる可能性がある。 $`A'_{\mathbf{s}} \equiv A_{\mathbf{s}} \cup \{ I_{\mathrm{a}} \}`$ $`A'_{\mathbf{a}} \equiv A_{\mathbf{a}} \cup \{ r \}`$ $`\boldsymbol{\sigma}'[r] \equiv \begin{cases} \varnothing &\text{if}\quad \boldsymbol{\sigma}[r] = \varnothing\ \wedge\ \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}} = 0\\ (\boldsymbol{\sigma}[r]_{\mathrm{n}}, \boldsymbol{\sigma}[r]_{\mathrm{b}} + \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}}, \boldsymbol{\sigma}[r]_{\mathbf{s}}, \boldsymbol{\sigma}[r]_{\mathrm{c}}) & \text{if}\quad r \neq I_{\mathrm{a}} \\ (\boldsymbol{\sigma}[r]_{\mathrm{n}}, 0, \boldsymbol{\sigma}[r]_{\mathbf{s}}, \boldsymbol{\sigma}[r]_{\mathrm{c}}) & \text{otherwise} \end{cases}`$ ここで $`r = \boldsymbol{\mu}_{\mathbf{s}}[0] \bmod 2^{160}`$ である。 $`\boldsymbol{\sigma}'[I_{\mathrm{a}}]_{\mathrm{b}} = 0`$ $`\begin{aligned} C_{\text{SELFDESTRUCT}}(\boldsymbol{\sigma}, \boldsymbol{\mu}) &\equiv G_{\mathrm{selfdestruct}} + \begin{cases} 0 & \text{if}\quad r \in A_{\mathbf{a}}\\ G_{\mathrm{coldaccountaccess}} & \text{otherwise} \end{cases}\\ &+ \begin{cases} G_{\mathrm{newaccount}} & \text{if}\quad \mathtt{DEAD}(\boldsymbol{\sigma}, r) \wedge \boldsymbol{\sigma}[I_{\mathrm{a}}]_{\mathrm{b}} \neq 0 \\ 0 & \text{otherwise} \end{cases} \end{aligned}`$ |

<span id="tnref-11"></span>[訳注11](#tn-11)

<span id="app:genesis"></span>

# 付録I. ジェネシス・ブロック

<div id="Genesis_Block">

</div>

ジェネシス・ブロックは15項目からなり、次のように規定される。

<span id="eq-333"></span>

```math
\big( \big( 0_{256}, \mathtt{KEC}\big(\mathtt{RLP}\big( () \big)\big), 0_{160}, stateRoot, 0, 0, 0_{2048}, 2^{34}, 0, 0, 3141592, time, 0, 0_{256},  \mathtt{KEC}\big( (42) \big) \big), (), () \big) \qquad \text{(333)}
```

ここで $`0_{256}`$ は、すべてゼロである256ビット・ハッシュの親ハッシュを指す。 $`0_{160}`$ は、すべてゼロである160ビット・ハッシュの受益者アドレスを指す。 $`0_{2048}`$ は、2048ビットすべてがゼロであるログ・ブルームを指す。 $`2^{34}`$ はdifficultyを指す。トランザクション・トライ・ルート、レシート・トライ・ルート、使用gas、ブロック番号、extraDataはいずれも $`0`$ であり、空バイト配列と等価である。ommer列とトランザクション列はいずれも空であり、 $`()`$ で表す。 $`\mathtt{KEC}\big( (42) \big)`$ は、nonceに用いる、最初で唯一のバイトの値が42である長さ1のバイト配列のKeccak-256ハッシュを指す。 $`\mathtt{KEC}\big(\mathtt{RLP}\big( () \big)\big)`$ の値は、RLPにおけるommerリストのハッシュを指し、両者とも空リストである。

概念実証版の系列には開発用プレマインが含まれるため、状態ルート・ハッシュはある値 $`stateRoot`$ となる。また $`time`$ にはジェネシス・ブロックの初期タイムスタンプが設定される。これらの値については最新の文書を参照されたい。

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

<span id="tnref-12"></span>[訳注12](#tn-12)

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

<span id="tnref-13"></span>[訳注13](#tn-13)

### J.4.2. キャッシュ

キャッシュ生成処理では、まずシード・ハッシュを用いて $`c_{\mathrm{size}}`$ バイトのメモリを順に埋め、次に[(Lerner 2014)](#ref-lerner2014randmemohash)が作成したRandMemoHashアルゴリズムを $`J_{\mathrm{cacherounds}}`$ 回適用する。単一バイト配列の配列である初期キャッシュ $`\mathbf{c'}`$ は、次のように構成される。

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

単一項目の計算では、場合によってXORの非結合的な代替として、FNVハッシュ（[(Glenn Fowler 1991)](#ref-FowlerNollVo1991FNVHash)）に着想を得たアルゴリズムを用いる。

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

<span id="tnref-14"></span>[訳注14](#tn-14)

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

<span id="tnref-15"></span>[訳注15](#tn-15)

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

# 付録K. メインネットワーク上の例外事象

## K.1. Gas 不足にもかかわらず生じたアカウント削除

ブロック2675119のトランザクション `0xcf416c536ec1a19ed1fb89e4ec7ffb3cf73aa413b3aa9b77d60e4fd81a4296ba` では、アドレス0x03のアカウントが呼び出され、その呼び出し中にgas不足が発生した。式（[209](#eq:pre)）に反して、これにより0x03が接触済みアドレス集合へ追加され、このトランザクションは $`\boldsymbol{\sigma}[0x03]`$ を $`\varnothing`$ に変えた。

# 付録L. 数学記号一覧

| 記号 | LaTeXコマンド | 説明 |
| --- | --- | --- |
| $`\bigvee`$ | `\bigvee` | 演算対象のすべての要素の最小上界、上限、または結びである。したがって、それらの要素のうち最大の要素となる（[(Davey and Priestley 2002)](#ref-Davey2002_zbMATH01748069)）。 |

<span id="tnref-16"></span>[訳注16](#tn-16)

<div id="translator-notes" class="translator-notes" role="doc-endnotes">

# 訳注（日本語訳で追加）

以下は翻訳時に加えた補足・疑義であり、原文の本文・付録・脚注には含まれない。原文の脚注番号1〜12とは独立した番号を用いる。

<div id="tn-1" class="translator-note" role="doc-endnote">

**訳注1（原文を保存）。** 第4.2節の定義では **init** を「サイズ無制限」としているが、[トランザクション実行の妥当性条件](#ch:transactions)では、コントラクト作成トランザクションの initcode を49152バイト以下に制限している。ここでは原文の記述を保存した。

[参照箇所へ戻る](#tnref-1)

</div>

<div id="tn-2" class="translator-note" role="doc-endnote">

**訳注2（原文を保存）。** 第4.3節の引き出しの直列化式の最後の成分は、原文では $`T_{\mathrm{a}}`$ となっている。同節の **amount** の定義からは $`W_{\mathrm{a}}`$ と考えられるが、ここでは原文の記号を保存した。

[参照箇所へ戻る](#tnref-2)

</div>

<div id="tn-3" class="translator-note" role="doc-endnote">

**訳注3（原文を保存・補足）。** 第4.4.4節の基本手数料増加時の式は増分 $`\nu`$ を最低1とするため、基本手数料が1 Weiから2 Weiへ増える場合など、増加率が12.5%を超えることもある。同節にある増加率の説明は原文のまま保存した。

[参照箇所へ戻る](#tnref-3)

</div>

<div id="tn-4" class="translator-note" role="doc-endnote">

**訳注4（原文を保存・補足）。** 第9.1節で、原文はメモリを「word-addressed byte array」と表現している。ただし、[命令一覧](#subsec:instruction-set)のMLOAD、MSTORE、MSTORE8の定義では、メモリの位置はバイト単位で指定される。32バイトのワードを読み書きする命令でも、指定位置が32の倍数である必要はない。

[参照箇所へ戻る](#tnref-4)

</div>

<div id="tn-5" class="translator-note" role="doc-endnote">

**訳注5（原文を保存）。** 第10.1節では、原文の予定時刻「2023-04-12 10:27:35 UTC」をそのまま記した。Ethereum Foundationの[当時の公式告知](https://blog.ethereum.org/2023/03/28/shapella-mainnet-announcement)では、同じエポック194,048の予定時刻は「2023-04-12 22:27:35 UTC」とされており、原文の時刻には誤記がある。

[参照箇所へ戻る](#tnref-5)

</div>

<div id="tn-6" class="translator-note" role="doc-endnote">

**訳注6（原文を保存・未解決の疑義）。** 付録E.1の楕円曲線の加算式には、無限遠点を表す $`(0,0)`$ を加法単位元として扱う規則が明記されていない。たとえば、相異なる点の式をそのまま $`(0,0)+(1,2)`$ に適用すると $`(3,-6)`$ となり、これは曲線の方程式を満たさない。無限遠点の符号化については [EIP-196](https://eips.ethereum.org/EIPS/eip-196#encoding) を参照されたい。

[参照箇所へ戻る](#tnref-6)

</div>

<div id="tn-7" class="translator-note" role="doc-endnote">

**訳注7（原文を保存・未解決の疑義）。** 付録E.1のペアリングの積は添字0から始まるが、同じ箇所に定義された点列は添字1から始まる。また、原文の検査条件は離散対数の積の和が $`1\bmod q`$ となることであり、同付録の $`\Xi_{\mathtt{SNARKV}}`$ も同じ条件を使う。一方、[EIP-197](https://eips.ethereum.org/EIPS/eip-197#specification) のプリコンパイルが検査するのは、この和が $`0\bmod q`$ 、すなわちペアリングの積が乗法単位元1となる条件である。本訳では原文の式を変更していない。

[参照箇所へ戻る](#tnref-7)

</div>

<div id="tn-8" class="translator-note" role="doc-endnote">

**訳注8（原文を保存・未解決の疑義）。** 付録E.1では、原文は $`G_T`$ を $`F_{q^{12}}`$ の乗法群としている。しかし、この群の位数 $`q^{12}-1`$ は $`q`$ の倍数ではないため、位数 $`q`$ の群からの非退化ペアリングについての同付録の説明とは整合しない。ここでも原文の $`q`$ を保存している。

[参照箇所へ戻る](#tnref-8)

</div>

<div id="tn-9" class="translator-note" role="doc-endnote">

**訳注9（原文を保存・未解決の疑義）。** 付録E.1の $`\Xi_{\mathtt{BN\_ADD}}`$ の定義に現れる $`\Xi_{\mathtt{BN\_PRE}}`$ は原文中で定義されていない。他のプリコンパイル済みコントラクトで使うテンプレートは $`\Xi_{\mathtt{PRE}}`$ である。

[参照箇所へ戻る](#tnref-9)

</div>

<div id="tn-10" class="translator-note" role="doc-endnote">

**訳注10（原文を保存・未解決の疑義）。** 付録E.2の範囲表記は、両端を含める本稿の一般的な規約と整合しない。たとえば $`I_{\mathbf{d}}[0..4]`$ はその規約では5バイトだが、 $`\mathtt{BE}_4(r)`$ は4バイトである。また、 $`\mathbb{B}_k`$ は本稿では $`k`$ バイトの列を表すのに対し、同付録の型の添字32・64・8はビット数に対応している。[EIP-152](https://eips.ethereum.org/EIPS/eip-152#specification) では $`r`$ は4バイト、各 $`h_i`$ ・ $`m_i`$ ・カウンタは8バイト、 $`f`$ は1バイトであり、全入力は213バイトとなる。

[参照箇所へ戻る](#tnref-10)

</div>

<div id="tn-11" class="translator-note" role="doc-endnote">

**訳注11（原文を保存・未解決の疑義）。** 付録H.2のCALLCODEとDELEGATECALLの説明中の引数番号は原文どおりである。ただし、第8節で定義する $`\Theta(\boldsymbol{\sigma}, A, s, o, r, c, g, p, v, \tilde v, \mathbf{d}, e, w)`$ では、宛先 $`r`$ は第5引数、送信者 $`s`$ は第3引数、実行文脈上の値 $`\tilde v`$ は第10引数であり、説明にある第4・第2・第9引数という番号と一致しない。

[参照箇所へ戻る](#tnref-11)

</div>

<div id="tn-12" class="translator-note" role="doc-endnote">

**訳注12（原文を保存・未解決の疑義）。** 付録J.3の説明はサイズの素数性を要求するが、原文の $`E_{\mathrm{prime}}`$ は $`x/y`$ が自然数かどうかだけを判定しており、素数判定を含まない。たとえば初期データセット・サイズを求める引数では $`x/y=2^{23}-1`$ は自然数なので、そのまま $`x`$ が返される。しかし、この商は $`47\times178481`$ と分解できる。

[参照箇所へ戻る](#tnref-12)

</div>

<div id="tn-13" class="translator-note" role="doc-endnote">

**訳注13（原文を保存・未解決の疑義）。** 付録J.4.1の説明文は最初のエポックのシードを「32バイトのゼロ列のKeccak-256ハッシュ」としているが、同小節の式はハッシュを取らず $`\mathbf{0}_{32}`$ 自体を返す。説明と式の相違をそのまま保存した。

[参照箇所へ戻る](#tnref-13)

</div>

<div id="tn-14" class="translator-note" role="doc-endnote">

**訳注14（原文を保存・未解決の疑義）。** 付録J.5のバイト順反転式では、原文の添字を保存した。0始まりの添字規約では、 $`i=0`$ の右辺は配列の範囲外となる。バイト順反転の添字なら通常は $`\lVert\mathbf{n}\rVert-1-i`$ となる。

[参照箇所へ戻る](#tnref-14)

</div>

<div id="tn-15" class="translator-note" role="doc-endnote">

**訳注15（原文を保存・未解決の疑義）。** 付録J.5の原文では $`E_{\mathrm{accesses}}`$ の左辺は4引数であるのに対し、再帰呼び出しは3引数であり、データセット $`\mathbf{d}`$ の引数が欠けている。式は原文のままとした。

[参照箇所へ戻る](#tnref-15)

</div>

<div id="tn-16" class="translator-note" role="doc-endnote">

**訳注16（原文を保存・未解決の疑義）。** 付録Lの数学記号一覧の説明の第2文は原文どおりだが、最小上界は元の要素の集合に属するとは限らず、一般にはその集合の最大要素ではない。たとえば包含関係で順序付けた集合族では、 $`\{1\}`$ と $`\{2\}`$ の結びは $`\{1,2\}`$ であり、元の二要素のいずれでもない。

[参照箇所へ戻る](#tnref-16)

</div>

</div>

[^1]: Shanghaiフォーク以降、ブロックが最終状態へ到達するには*引き出し操作*も処理する必要がある。引き出し操作は[第4.3節](#subsec:The_Withdrawal)で定義し、ブロックの最終状態は[第12節](#ch:finalisation)で詳しく論じる。

[^2]: Paris、Shanghaiおよび今後の各フォークは、あるブロック番号（たとえばParisでは15,537,394）で有効になったものの、トリガーはブロック番号ではなく、指定された*タイムスタンプ*（Parisでは*総難易度*）への到達であった。*Paris* 以降のハードフォークのトリガーは[第10節](#ch:pos_transition)で詳しく論じる。

[^3]: 特に、このような「道具」は最終的に、人間による開始から因果的に大きく切り離されるか、人間が因果的に極めて中立となり、自律的主体とみなすのが正当な段階へ達する可能性がある。たとえばコントラクトが、自身の実行を開始するトランザクションを送る人間へ報奨金を提示する場合があり得る。

[^4]: *優先手数料*については[第5節](#ch:payment)および[第6節](#ch:transactions)で詳しく論じる。

[^5]: 型0および型1トランザクションは、 $`T_{\mathrm{m}}`$ と $`T_{\mathrm{f}}`$ を $`T_{\mathrm{p}}`$ の値に設定した型2トランザクションと同じgas価格の挙動を示す。

[^6]: *ommer* は「親のきょうだい」を意味するジェンダー中立な用語である。<https://nonbinary.miraheze.org/wiki/Gender_neutral_language_in_English#Aunt/Uncle>を参照されたい。

[^7]: RANDAOはEthereum合意レイヤーのバリデータが生成する疑似乱数値である。RANDAOの詳細は合意レイヤー仕様（<https://github.com/ethereum/consensus-specs>）を参照されたい。

[^8]: 2048 $`= 2^{11}`$ （11ビット）であり、下位11ビットはオペランドを2048で割った剰余である。この場合のオペランドは「バイト列のKeccak-256ハッシュの先頭三つの各2バイト対」である。

[^9]: gasの最大還付割合は、*London* リリースにおいて[(Buterin and Swende 2021)](#ref-EIP-3529)によるEIP-3529で2分の1から5分の1へ引き下げられた。

[^10]: トランザクションが直接引き起こしたのではなく、EVMコードの実行から生じたメッセージ呼び出しまたはコントラクト作成の場合、これは送信者と異なり得る。

[^11]: 初期化コードの実行中、そのアドレスに対する `EXTCODESIZE` はアカウントのコード長であるゼロを返し、`CODESIZE` は初期化コードの長さを返すべきである（[付録H.2](#subsec:instruction-set)で定義）。

[^12]: *LMD GHOST* は「Latest Message Driven」と「Greedy Heaviest-Observed Sub-Tree」という二つの頭字語からなる。
