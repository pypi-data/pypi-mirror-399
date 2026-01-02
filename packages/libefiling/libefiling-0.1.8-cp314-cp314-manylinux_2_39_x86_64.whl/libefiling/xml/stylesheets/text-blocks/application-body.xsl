<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:jp="http://www.jpo.go.jp"
    xmlns:f="urn:libefiling:string-utils"
    exclude-result-prefixes="xs jp f">

    <xsl:include href="common-templates/string-utils.xsl" />

    <xsl:variable name="law">
        <xsl:choose>
            <xsl:when
                test="//procedure-param[@name='law' and text() = '1']">patent</xsl:when>
            <xsl:when
                test="//procedure-param[@name='law' and text() = '2']">utility-model</xsl:when>
            <xsl:otherwise>unknown</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:template match="/">
        <xsl:element name="root">
            <xsl:apply-templates select="root/application-body/description" />
            <xsl:apply-templates select="root/application-body/claims" />
            <xsl:apply-templates select="root/application-body/abstract" />
            <xsl:apply-templates select="root/application-body/drawings" />
        </xsl:element>
    </xsl:template>

    <!-- 明細書 -->
    <xsl:template
        match="description">
        <xsl:element name="blocks">
            <xsl:element name="tag">description</xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of select="key('tags-table-key', 'description', $tags-table)/@jp-tag" />
            </xsl:element>
            <xsl:apply-templates />

            <xsl:element name="indentLevel">0</xsl:element>
        </xsl:element>
    </xsl:template>

    <!-- 発明/考案の名称 -->
    <xsl:template
        match="invention-title">
        <xsl:element name="blocks">
            <xsl:element name="tag">
                <xsl:value-of
                    select="key('tags-table-key', name() || '-' || $law, $tags-table)/@camel-tag" />
            </xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of
                    select="key('tags-table-key', name() || '-' || $law, $tags-table)/@jp-tag" />
            </xsl:element>
            <xsl:element name="text">
                <xsl:value-of select="." />
            </xsl:element>
            <xsl:element name="indentLevel">0</xsl:element>
        </xsl:element>
    </xsl:template>

    <!-- 特実で切り分けが不要な要素  -->
    <!-- 技術分野, 背景技術, 先行技術文献，特許文献，非特許文献，
         解決手段、図面の簡単な説明
         産業上の利用可能性, 配列表,符号の説明,受託番号 -->
    <xsl:template
        match="technical-field | background-art |
        citation-list | patent-literature | non-patent-literature |
        tech-solution | description-of-drawings |
        industrial-applicability | sequence-list-text | reference-signs-list |
        reference-to-deposited-biological-material">
        <xsl:element name="blocks">
            <xsl:element name="tag">
                <xsl:value-of select="key('tags-table-key', name(), $tags-table)/@camel-tag" />
            </xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of select="key('tags-table-key', name(), $tags-table)/@jp-tag" />
            </xsl:element>
            <xsl:if test="*[1]">
                <xsl:apply-templates />
            </xsl:if>
            <xsl:element name="indentLevel">0</xsl:element>
        </xsl:element>
    </xsl:template>

    <!-- 特実で切り分けが必要な要素  -->
    <!-- 解決しようとする課題,  効果, 実施形態 -->
    <xsl:template
        match="summary-of-invention | disclosure |
        tech-problem | advantageous-effects |
        description-of-embodiments | best-mode">
        <xsl:element name="blocks">
            <xsl:element name="tag">
                <xsl:value-of
                    select="key('tags-table-key', name() || '-' || $law, $tags-table)/@camel-tag" />
            </xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of
                    select="key('tags-table-key', name() || '-' || $law, $tags-table)/@jp-tag" />
            </xsl:element>
            <xsl:if test="*[1]">
                <xsl:apply-templates />
            </xsl:if>
            <xsl:element name="indentLevel">0</xsl:element>
        </xsl:element>
    </xsl:template>

    <!-- 特許文献 -->
    <xsl:template
        match="patcit">
        <xsl:element name="blocks">
            <xsl:element name="tag">patcit</xsl:element>
            <xsl:element name="number">
                <xsl:value-of select="@num" />
            </xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of select="'【特許文献' || f:to-fullwidth-digit(@num) || '】'" />
            </xsl:element>
            <xsl:element name="text">
                <xsl:value-of select="./text" />
            </xsl:element>
            <xsl:element name="indentLevel">2</xsl:element>
        </xsl:element>
    </xsl:template>

    <!-- 非特許文献 -->
    <xsl:template
        match="nplcit">
        <xsl:element name="blocks">
            <xsl:element name="tag">nplcit</xsl:element>
            <xsl:element name="number">
                <xsl:value-of select="@num" />
            </xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of select="'【非特許文献' || f:to-fullwidth-digit(@num) || '】'" />
            </xsl:element>
            <xsl:element name="text">
                <xsl:value-of select="./text" />
            </xsl:element>
            <xsl:element name="indentLevel">2</xsl:element>
        </xsl:element>
    </xsl:template>

    <!-- 図面の簡単な説明 の図 -->
    <xsl:template
        match="figref">
        <xsl:element name="blocks">
            <xsl:element name="tag">figref</xsl:element>
            <xsl:element name="number">
                <xsl:value-of select="@num" />
            </xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of select="'【図' || f:to-fullwidth-digit(@num) || '】'" />
            </xsl:element>
            <xsl:element name="text">
                <xsl:value-of select="." />
            </xsl:element>
            <xsl:element name="indentLevel">2</xsl:element>
        </xsl:element>
    </xsl:template>

    <!-- 実施例 -->
    <xsl:template match="embodiments-example">
        <xsl:element name="blocks">
            <xsl:element name="tag">embodimentExample</xsl:element>
            <xsl:element name="number">
                <xsl:value-of select="@ex-num" />
            </xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of select="'【実施例】'" />
            </xsl:element>
            <xsl:apply-templates select="p" />
            <xsl:element name="indentLevel">1</xsl:element>
        </xsl:element>
    </xsl:template>

    <!-- 実施例 -->
    <xsl:template match="mode-for-invention">
        <xsl:element name="blocks">
            <xsl:element name="tag">modeForInvention</xsl:element>
            <xsl:element name="number">
                <xsl:value-of select="@mode-num" />
            </xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of select="'【実施例' || f:to-fullwidth-digit(@mode-num) || '】'" />
            </xsl:element>
            <xsl:apply-templates select="p" />
            <xsl:element name="indentLevel">1</xsl:element>
        </xsl:element>
    </xsl:template>

    <!-- 特許請求の範囲/実用新案登録請求の範囲 -->
    <xsl:template match="claims">
        <xsl:element name="blocks">
            <xsl:element name="tag">claims</xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of
                    select="key('tags-table-key', 'claims-' || $law, $tags-table)/@jp-tag" />
            </xsl:element>
            <xsl:element name="indentLevel">0</xsl:element>
            <xsl:apply-templates />
        </xsl:element>
    </xsl:template>

    <!-- 請求項 -->
    <xsl:template match="claim">
        <xsl:element name="blocks">
            <xsl:element name="tag">claim</xsl:element>
            <xsl:element name="jpTag">【請求項<xsl:value-of select="f:to-fullwidth-digit(@num)" />】</xsl:element>
            <xsl:element name="number">
                <xsl:value-of select="@num" />
            </xsl:element>
            <xsl:element name="indentLevel">0</xsl:element>
            <xsl:element name="isIndependent">
                <xsl:choose>
                    <xsl:when test="claim-text[contains(., '請求項')]">false</xsl:when>
                    <xsl:otherwise>true</xsl:otherwise>
                </xsl:choose>
            </xsl:element>
            <xsl:apply-templates />
        </xsl:element>
    </xsl:template>

    <!-- 請求項の文言 -->
    <xsl:template match="claim-text">
        <xsl:element name="blocks">
            <xsl:element name="tag">claimText</xsl:element>
            <xsl:apply-templates />
        </xsl:element>
    </xsl:template>

    <!-- 図面 -->
    <xsl:template match="drawings">
        <xsl:element name="blocks">
            <xsl:element name="tag">drawings</xsl:element>
            <xsl:element name="indentLevel">0</xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of select="key('tags-table-key', 'drawings', $tags-table)/@jp-tag" />
            </xsl:element>
            <xsl:apply-templates select="figure" />
        </xsl:element>
    </xsl:template>

    <!-- 要約書 -->
    <xsl:template match="abstract">
        <xsl:element name="blocks">
            <xsl:element name="tag">abstract</xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of select="key('tags-table-key', 'abstract', $tags-table)/@jp-tag" />
            </xsl:element>
            <xsl:element name="text">
                <xsl:call-template name="trim">
                    <xsl:with-param name="text" select="." />
                </xsl:call-template>
            </xsl:element>
            <xsl:element name="indentLevel">0</xsl:element>
        </xsl:element>
    </xsl:template>

    <!--  図   -->
    <xsl:template match="figure">
        <!-- figref[@num=@num] だと集合値の比較なので失敗する 
         変数にすると単一値の比較になるので意図通りになる
         figref[@num=current()/@num] でも可
          -->
        <xsl:variable name="num" select="@num" />

        <!-- 子要素img のファイル名 -->
        <xsl:variable name="image-file" select="img/@file" />

        <xsl:element name="blocks">
            <xsl:element name="tag">
                <xsl:value-of select="key('tags-table-key', name(), $tags-table)/@camel-tag" />
            </xsl:element>
            <xsl:element name="number">
                <xsl:value-of select="@num" />
            </xsl:element>
            <xsl:element name="jpTag">
                <xsl:text>【</xsl:text>
                <xsl:value-of
                    select="key('tags-table-key', name(), $tags-table)/@jp-tag" />
                <xsl:value-of select="f:to-fullwidth-digit(@num)" />
                <xsl:text>】</xsl:text>
            </xsl:element>
            <xsl:element name="alt">
                <xsl:value-of select="name() || ' No. ' || @num || ' '" />
                <xsl:value-of
                    select="//description-of-drawings//figref[@num=$num]" />
            </xsl:element>

            <xsl:element name="representative">
                <xsl:choose>
                    <xsl:when test="//procedure-param[@file-name = $image-file]">true</xsl:when>
                    <xsl:otherwise>false</xsl:otherwise>
                </xsl:choose>
            </xsl:element>

            <xsl:element name="indentLevel">0</xsl:element>

            <xsl:apply-templates select="img" />
        </xsl:element>
    </xsl:template>

    <!--  化,表,数   -->
    <xsl:template match="chemistry | tables | maths">
        <xsl:element name="blocks">
            <xsl:element name="tag">
                <xsl:value-of select="key('tags-table-key', name(), $tags-table)/@camel-tag" />
            </xsl:element>
            <xsl:element name="number">
                <xsl:value-of select="@num" />
            </xsl:element>
            <xsl:element name="jpTag">
                <xsl:text>【</xsl:text>
                <xsl:value-of
                    select="key('tags-table-key', name(), $tags-table)/@jp-tag" />
                <xsl:value-of select="f:to-fullwidth-digit(@num)" />
                <xsl:text>】</xsl:text>
            </xsl:element>

            <xsl:element name="indentLevel">2</xsl:element>

            <xsl:apply-templates select="img" />
        </xsl:element>
    </xsl:template>


    <!-- 変換元XMLにある images/image のlookup -->
    <xsl:key name="images-table-key" match="/root/images/image" use="@orig" />

    <!--  イメージ   -->
    <xsl:template match="img">
        <xsl:for-each select="key('images-table-key', @file)">
            <xsl:element name="images">
                <xsl:element name="src">
                    <xsl:value-of select="@new" />
                </xsl:element>
                <xsl:element name="width">
                    <xsl:value-of select="@width" />
                </xsl:element>
                <xsl:element name="height">
                    <xsl:value-of select="@height" />
                </xsl:element>
                <xsl:element name="kind">
                    <xsl:value-of select="@kind" />
                </xsl:element>
                <xsl:element name="sizeTag">
                    <xsl:value-of select="@sizeTag" />
                </xsl:element>
            </xsl:element>
        </xsl:for-each>
    </xsl:template>

    <!-- 段落 -->
    <xsl:template
        match="p">
        <xsl:element name="blocks">
            <xsl:element name="tag">paragraph</xsl:element>
            <xsl:element name="indentLevel">1</xsl:element>
            <xsl:element name="number">
                <xsl:value-of select="@num" />
            </xsl:element>
            <xsl:element name="jpTag">
                <xsl:value-of select="'【' || f:to-fullwidth-digit(@num) || '】'" />
            </xsl:element>
            <xsl:apply-templates />
        </xsl:element>
    </xsl:template>

    <xsl:template
        match="text() | sup | sub | u">
        <xsl:variable name="tag">
            <xsl:choose>
                <xsl:when test="self::text()">text</xsl:when>
                <xsl:when test="self::sup">sup</xsl:when>
                <xsl:when test="self::sub">sub</xsl:when>
                <xsl:when test="self::u">underline</xsl:when>
            </xsl:choose>
        </xsl:variable>

        <!-- 次の「有意ノード」を見る -->
        <xsl:variable name="nextNode"
            select="following-sibling::node()[not(self::text()[normalize-space(.)=''])][1]" />

        <!-- 次が br か、次が存在しない（p末尾）なら true -->
        <xsl:variable name="isLastSentence"
            select="if (empty($nextNode) or $nextNode/self::br) then 'true' else 'false'" />

        <xsl:if test="normalize-space() != ''">
            <xsl:element name="blocks">
                <xsl:element name="tag">
                    <xsl:value-of select="$tag" />
                </xsl:element>
                <xsl:element name="text">
                    <xsl:call-template name="trim">
                        <xsl:with-param name="text" select="." />
                    </xsl:call-template>
                </xsl:element>
                <xsl:element name="isLastSentence">
                    <xsl:value-of select="$isLastSentence" />
                </xsl:element>
            </xsl:element>
        </xsl:if>
    </xsl:template>

    <xsl:template name="text-node">
        <xsl:param name="text" as="xs:string" />
        <xsl:param name="is-last" as="xs:boolean" />
        <xsl:if test="normalize-space($text) != ''">
            <xsl:element name="blocks">
                <xsl:element name="tag">text</xsl:element>
                <xsl:element name="text">
                    <xsl:call-template name="trim">
                        <xsl:with-param name="text" select="." />
                    </xsl:call-template>
                </xsl:element>
                <xsl:element name="isLast">
                    <xsl:value-of select="$is-last" />
                </xsl:element>
            </xsl:element>
        </xsl:if>
    </xsl:template>


    <xsl:key name="tags-table-key" match="item" use="@tag" />
    <xsl:variable name="tags-table">
        <item tag="description" camel-tag="description" jp-tag="【書類名】 明細書" />
        <item tag="claims-patent" camel-tag="claims" jp-tag="【書類名】 特許請求の範囲" />
        <item tag="claims-utility-model" camel-tag="claims" jp-tag="【書類名】 実用新案登録請求の明細書" />
        <item tag="drawings" camel-tag="drawings" jp-tag="【書類名】 図面" />
        <item tag="abstract" camel-tag="abstract" jp-tag="【書類名】 要約書" />
        <item tag="invention-title-patent" camel-tag="inventionTitle" jp-tag="【発明の名称】" />
        <item tag="invention-title-utility-model" camel-tag="inventionTitle"
            jp-tag="【考案の名称】" />
        <item tag="technical-field" camel-tag="technicalField" jp-tag="【技術分野】" />
        <item tag="background-art" camel-tag="backgroundArt" jp-tag="【背景技術】" />
        <item tag="citation-list" camel-tag="citationList" jp-tag="【先行技術文献】" />
        <item tag="patent-literature" camel-tag="patentLiterature" jp-tag="【特許文献】" />
        <item tag="non-patent-literature" camel-tag="nonPatentLiterature" jp-tag="【非特許文献】" />
        <item tag="disclosure-patent" camel-tag="disclosure" jp-tag="【発明の開示】" />
        <item tag="disclosure-utility-model" camel-tag="disclosure" jp-tag="【考案の開示】" />
        <item tag="summary-of-invention-patent" camel-tag="summaryOfInvention"
            jp-tag="【発明の概要】" />
        <item tag="summary-of-invention-utility-model" camel-tag="summaryOfInvention"
            jp-tag="【考案の概要】" />
        <item tag="tech-problem-patent" camel-tag="techProblem" jp-tag="【発明が解決しようとする課題】" />
        <item tag="tech-problem-utility-model" camel-tag="techProblem"
            jp-tag="【考案が解決しようとする課題】" />
        <item tag="tech-solution" camel-tag="techSolution" jp-tag="【課題を解決する手段】" />
        <item tag="advantageous-effects-patent" camel-tag="advantageousEffects"
            jp-tag="【発明の効果】" />
        <item tag="advantageous-effects-utility-model" camel-tag="advantageousEffects"
            jp-tag="【考案の効果】" />
        <item tag="description-of-drawings" camel-tag="descriptionOfDrawings" jp-tag="【図面の簡単な説明】" />
        <item tag="description-of-embodiments-patent" camel-tag="descriptionOfEmbodiments"
            jp-tag="【発明を実施するための形態】" />
        <item tag="description-of-embodiments-utility-model"
            camel-tag="descriptionOfEmbodiments" jp-tag="【考案を実施するための形態】" />
        <item tag="best-mode-patent" camel-tag="bestMode" jp-tag="【発明を実施するための最良の形態】" />
        <item tag="best-mode-utility-model" camel-tag="bestMode"
            jp-tag="【考案を実施するための最良の形態】" />
        <item tag="sequence-list-text" camel-tag="sequenceListText" jp-tag="【配列表】" />
        <item tag="industrial-applicability" camel-tag="industrialApplicability"
            jp-tag="【産業上の利用可能性】" />
        <item tag="reference-signs-list" camel-tag="referenceSignsList" jp-tag="【符号の説明】" />
        <item tag="sequence-list-text" camel-tag="sequenceListText" jp-tag="【配列表フリーテキスト】" />
        <item tag="reference-to-deposited-biological-material"
            camel-tag="referenceToDepositedBiologicalMaterial" jp-tag="【受託番号】" />
        <item tag="figure" camel-tag="figure" jp-tag="図" />
        <item tag="chemistry" camel-tag="chemistry" jp-tag="化" />
        <item tag="tables" camel-tag="tables" jp-tag="表" />
        <item tag="maths" camel-tag="maths" jp-tag="数" />
    </xsl:variable>

    <!-- 先頭と最後の空白/改行の除去 -->
    <xsl:template
        name="trim">
        <xsl:param name="text" />
        <xsl:value-of select="replace($text, '^[\s]+|[\s]+$', '')" />
    </xsl:template>

</xsl:stylesheet>