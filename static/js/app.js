/* =====================================================
   东方智行 · Enterprise AI Workbench
   Frontend Application
===================================================== */


/* =====================================================
   1. Global State
===================================================== */

let currentPage = "dashboard";

let sessions = [];

let lastWorkflowSteps = [];

let agentBusy = false;


/* =====================================================
   2. Page Configuration
===================================================== */

const pageConfig = {

    dashboard: {
        title: "企业 AI 工作台",
        description: "企业级知识、Agent 与 Workflow 工作空间"
    },

    knowledge: {
        title: "企业知识库",
        description: "基于 RAG 的企业知识检索与知识资产管理"
    },

    agent: {
        title: "AI Agent",
        description: "企业差旅智能助手 · RAG + Tool Calling + Workflow"
    },

    workflow: {
        title: "Agent Workflow",
        description: "任务规划、知识检索、工具调用与执行轨迹"
    },

    sessions: {
        title: "最近会话",
        description: "查看近期 AI Agent 对话与执行记录"
    }

};


/* =====================================================
   3. DOM Ready
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeApp();

    }
);


/* =====================================================
   4. Initialize Application
===================================================== */

async function initializeApp() {

    console.log(
        "东方智行 Enterprise AI Workbench 初始化..."
    );


    initializeNavigation();

    initializeQuickActions();

    initializeAgentInput();

    initializeClickableElements();


    await loadPage("dashboard");


    /*
       页面启动后顺便加载最近会话，
       这样 Dashboard 可以显示最近对话。
    */

    await loadSessions();


    console.log(
        "Enterprise AI Workbench 初始化完成"
    );

}


/* =====================================================
   5. Navigation
===================================================== */

function initializeNavigation() {

    const navItems =
        document.querySelectorAll(
            "[data-page]"
        );


    navItems.forEach(
        function (item) {

            item.addEventListener(
                "click",
                function () {

                    const page =
                        item.dataset.page;


                    if (!page) {

                        return;

                    }


                    loadPage(page);

                }
            );

        }
    );

}


/* =====================================================
   6. Clickable Elements
===================================================== */

function initializeClickableElements() {

    const clickableItems =
        document.querySelectorAll(
            ".clickable[data-page]"
        );


    clickableItems.forEach(
        function (item) {

            item.addEventListener(
                "click",
                function () {

                    const page =
                        item.dataset.page;


                    if (page) {

                        loadPage(page);

                    }

                }
            );

        }
    );

}


/* =====================================================
   7. Load Page
===================================================== */

async function loadPage(page) {

    currentPage = page;


    updateNavigation(page);

    updatePageHeader(page);

    showPage(page);


    switch (page) {


        case "dashboard":

            await loadDashboard();

            break;


        case "knowledge":

            await loadKnowledgeBase();

            break;


        case "agent":

            initializeAgentPage();

            break;


        case "workflow":

            await loadWorkflow();

            break;


        case "sessions":

            await loadSessions();

            break;


        default:

            console.warn(
                "未知页面：",
                page
            );

    }

}


/* =====================================================
   8. Show Page
===================================================== */

function showPage(page) {

    const pages =
        document.querySelectorAll(
            ".page"
        );


    pages.forEach(
        function (item) {

            item.classList.remove(
                "active"
            );

        }
    );


    const target =
        document.getElementById(
            "page-" + page
        );


    if (target) {

        target.classList.add(
            "active"
        );

    }

}


/* =====================================================
   9. Update Navigation
===================================================== */

function updateNavigation(page) {

    const navItems =
        document.querySelectorAll(
            ".nav-item[data-page]"
        );


    navItems.forEach(
        function (item) {

            item.classList.remove(
                "active"
            );


            if (
                item.dataset.page === page
            ) {

                item.classList.add(
                    "active"
                );

            }

        }
    );

}


/* =====================================================
   10. Update Header
===================================================== */

function updatePageHeader(page) {

    const config =
        pageConfig[page];


    if (!config) {

        return;

    }


    setText(
        "pageTitle",
        config.title
    );


    setText(
        "pageDescription",
        config.description
    );

}


/* =====================================================
   11. Dashboard
===================================================== */

async function loadDashboard() {

    try {

        const response =
            await fetch(
                "/api/dashboard"
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                "Dashboard 数据加载失败"
            );

        }


        updateDashboard(data);


    } catch (error) {

        console.error(
            "Dashboard 加载失败：",
            error
        );

    }

}


/* =====================================================
   12. Update Dashboard
===================================================== */

function updateDashboard(data) {

    setText(
        "agentStatus",
        data.agent_status || "Online"
    );


    setText(
        "knowledgeDocuments",
        data.knowledge_documents ?? "-"
    );


    setText(
        "knowledgeChunks",
        data.knowledge_chunks ?? "-"
    );


    setText(
        "toolCount",
        data.tools ?? "-"
    );


    setText(
        "embeddingModel",
        data.embedding_model || "-"
    );


    setText(
        "vectorDimension",
        data.vector_dimension ?? "-"
    );


    setText(
        "sidebarKnowledgeCount",
        data.knowledge_documents ?? "-"
    );


    renderDashboardSessions(
        sessions
    );

}


/* =====================================================
   13. Dashboard Recent Sessions
===================================================== */

function renderDashboardSessions(items) {

    const container =
        document.getElementById(
            "dashboardSessions"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    if (
        !items ||
        items.length === 0
    ) {

        container.innerHTML = `
            <div class="conversation-empty">
                暂无最近会话
            </div>
        `;

        return;

    }


    const recent =
        items.slice(0, 4);


    recent.forEach(
        function (session) {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "conversation";


            item.innerHTML = `
                <div class="conversation-question">
                    ${escapeHtml(
                        session.question || ""
                    )}
                </div>

                <div class="conversation-time">
                    ${formatDuration(
                        session.duration_ms
                    )}
                </div>
            `;


            item.addEventListener(
                "click",
                function () {

                    loadPage("agent");

                }
            );


            container.appendChild(
                item
            );

        }
    );

}


/* =====================================================
   14. Knowledge Base
===================================================== */

async function loadKnowledgeBase() {

    try {

        const response =
            await fetch(
                "/api/knowledge"
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                "Knowledge Base 数据加载失败"
            );

        }


        updateKnowledgeBase(data);


    } catch (error) {

        console.error(
            "Knowledge Base 加载失败：",
            error
        );

    }

}


/* =====================================================
   15. Update Knowledge Base
===================================================== */

function updateKnowledgeBase(data) {

    setText(
        "kbDocumentCount",
        data.total_documents ?? "-"
    );


    setText(
        "kbChunkCount",
        data.total_chunks ?? "-"
    );


    setText(
        "embeddingModel",
        data.embedding_model || "-"
    );


    setText(
        "sidebarKnowledgeCount",
        data.total_documents ?? "-"
    );


    const container =
        document.getElementById(
            "knowledgeDocumentList"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    if (
        !data.documents ||
        data.documents.length === 0
    ) {

        container.innerHTML = `
            <div class="workflow-empty">

                <div class="workflow-empty-icon">
                    ▤
                </div>

                <div>
                    暂无知识库文档
                </div>

            </div>
        `;

        return;

    }


    data.documents.forEach(
        function (doc) {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "conversation";


            card.innerHTML = `
                <div class="conversation-question">
                    ${escapeHtml(
                        doc.name || "企业知识库文档"
                    )}
                </div>

                <div class="conversation-time">

                    ${escapeHtml(
                        doc.type || "PDF"
                    )}

                    ·

                    ${doc.chunks ?? 0}
                    Chunks

                    ·

                    ${escapeHtml(
                        doc.embedding_model || "-"
                    )}

                    ·

                    ${doc.vector_dimension ?? "-"}
                    Dimensions

                </div>
            `;


            container.appendChild(
                card
            );

        }
    );

}


/* =====================================================
   16. Agent Page
===================================================== */

function initializeAgentPage() {

    initializeAgentInput();

}


/* =====================================================
   17. Agent Input
===================================================== */

function initializeAgentInput() {

    const input =
        document.getElementById(
            "question"
        );


    const button =
        document.getElementById(
            "sendButton"
        );


    if (
        input &&
        !input.dataset.initialized
    ) {

        input.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    sendAgentMessage();

                }

            }
        );


        input.dataset.initialized =
            "true";

    }


    if (
        button &&
        !button.dataset.initialized
    ) {

        button.addEventListener(
            "click",
            function () {

                sendAgentMessage();

            }
        );


        button.dataset.initialized =
            "true";

    }

}


/* =====================================================
   18. Send Agent Message
===================================================== */

async function sendAgentMessage() {

    if (agentBusy) {

        return;

    }


    const input =
        document.getElementById(
            "question"
        );


    const button =
        document.getElementById(
            "sendButton"
        );


    if (!input) {

        console.error(
            "找不到 question 输入框"
        );

        return;

    }


    const message =
        input.value.trim();


    if (!message) {

        return;

    }


    agentBusy = true;


    if (button) {

        button.disabled = true;

        button.textContent =
            "处理中";

    }


    /*
       确保发送消息时自动进入 Agent 页面。
    */

    if (currentPage !== "agent") {

        await loadPage("agent");

    }


    /*
       用户消息
    */

    appendChatMessage(
        "user",
        message
    );


    input.value = "";


    /*
       Thinking Bubble
    */

    const thinkingId =
        appendThinkingMessage();


    /*
       重置 Workflow
    */

    renderWorkflowSteps(
        [],
        "RUNNING"
    );


    showAgentStatus(
        "正在分析需求..."
    );


    try {

        const response =
            await fetch(
                "/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message: message
                        })
                }
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                "Agent 请求失败"
            );

        }


        /*
           更新 AI 回复
        */

        updateChatMessage(
            thinkingId,
            data.answer || "Agent 未返回回答。"
        );


        /*
           Agent Steps
        */

        const steps =
            normalizeSteps(
                data.steps || []
            );


        lastWorkflowSteps =
            steps;


        renderWorkflowSteps(
            steps,
            "COMPLETED"
        );


        /*
           Sources
        */

        renderSources(
            data.sources || []
        );


        /*
           Execution Duration
        */

        setText(
            "agentDuration",
            "Total Runtime · " +
            formatDuration(
                data.total_duration_ms
            )
        );


        showAgentStatus(
            "任务完成"
        );


        /*
           更新 Workflow 页面
        */

        if (currentPage === "workflow") {

            renderWorkflowSteps(
                steps,
                "COMPLETED"
            );

        }


        /*
           更新 Session
        */

        await loadSessions();


    } catch (error) {

        console.error(
            "Agent 请求失败：",
            error
        );


        updateChatMessage(
            thinkingId,
            "抱歉，Agent 暂时无法处理这个请求。"
        );


        renderWorkflowError(
            error.message
        );


        showAgentStatus(
            "执行失败"
        );


    } finally {

        agentBusy = false;


        if (button) {

            button.disabled = false;

            button.textContent =
                "发送";

        }

    }

}


/* =====================================================
   19. Thinking Message
===================================================== */

function appendThinkingMessage() {

    const container =
        document.getElementById(
            "chatMessages"
        );


    if (!container) {

        return null;

    }


    const message =
        document.createElement(
            "div"
        );


    message.className =
        "message ai";


    const id =
        createMessageId();


    message.id = id;


    message.innerHTML = `
        <div class="message-bubble">

            <div class="ai-thinking">

                <span></span>
                <span></span>
                <span></span>

                <span style="margin-left:6px;">
                    Agent 正在思考
                </span>

            </div>

        </div>
    `;


    container.appendChild(
        message
    );


    scrollChatToBottom();


    return id;

}


/* =====================================================
   20. Append Chat Message
===================================================== */

function appendChatMessage(
    role,
    text
) {

    const container =
        document.getElementById(
            "chatMessages"
        );


    if (!container) {

        return null;

    }


    const message =
        document.createElement(
            "div"
        );


    message.className =
        role === "user"
            ? "message user"
            : "message ai";


    const id =
        createMessageId();


    message.id = id;


    message.innerHTML = `
        <div class="message-bubble">
            ${formatAnswer(text)}
        </div>
    `;


    container.appendChild(
        message
    );


    scrollChatToBottom();


    return id;

}


/* =====================================================
   21. Update Chat Message
===================================================== */

function updateChatMessage(
    id,
    text
) {

    const message =
        document.getElementById(
            id
        );


    if (!message) {

        return;

    }


    const bubble =
        message.querySelector(
            ".message-bubble"
        );


    if (!bubble) {

        return;

    }


    bubble.innerHTML =
        formatAnswer(text);


    scrollChatToBottom();

}


/* =====================================================
   22. Scroll Chat
===================================================== */

function scrollChatToBottom() {

    const container =
        document.getElementById(
            "chatMessages"
        );


    if (!container) {

        return;

    }


    setTimeout(
        function () {

            container.scrollTop =
                container.scrollHeight;

        },
        20
    );

}


/* =====================================================
   23. Normalize Agent Steps
===================================================== */

function normalizeSteps(steps) {

    if (
        !Array.isArray(steps)
    ) {

        return [];

    }


    const result = [];


    steps.forEach(
        function (step) {

            if (!step) {

                return;

            }


            const tool =
                step.tool ||
                step.name ||
                "";


            /*
               如果后端产生连续重复工具调用，
               前端视觉上进行合并。
            */

            const previous =
                result[result.length - 1];


            if (
                previous &&
                previous.tool === tool &&
                tool === "calculate_travel_expense"
            ) {

                previous.duration_ms =
                    Number(
                        previous.duration_ms || 0
                    ) +
                    Number(
                        step.duration_ms || 0
                    );

                return;

            }


            result.push({

                ...step,

                tool: tool

            });

        }
    );


    return result;

}


/* =====================================================
   24. Workflow Steps
===================================================== */

function renderWorkflowSteps(
    steps,
    status = "COMPLETED"
) {

    const containers = [
        document.getElementById(
            "workflowSteps"
        ),
        document.getElementById(
            "agentSteps"
        )
    ];


    containers.forEach(
        function (container) {

            if (!container) {

                return;

            }


            container.innerHTML = "";


            if (
                status === "RUNNING" &&
                steps.length === 0
            ) {

                container.innerHTML = `
                    <div class="workflow-running">

                        <div class="workflow-loading-spinner"></div>

                        <div>

                            <div class="workflow-running-title">
                                Agent 正在执行任务
                            </div>

                            <div class="workflow-running-desc">
                                正在进行任务规划、知识检索与工具调用
                            </div>

                        </div>

                    </div>
                `;

                return;

            }


            if (
                !steps ||
                steps.length === 0
            ) {

                container.innerHTML = `
                    <div class="workflow-empty">

                        <div class="workflow-empty-icon">
                            ⟡
                        </div>

                        <div>
                            暂无执行记录
                        </div>

                        <div class="workflow-empty-desc">
                            在 AI Agent 页面发送问题后，
                            这里将展示完整执行轨迹
                        </div>

                    </div>
                `;

                return;

            }


            steps.forEach(
                function (step, index) {

                    const item =
                        document.createElement(
                            "div"
                        );


                    item.className =
                        "workflow-step";


                    const node =
                        document.createElement(
                            "div"
                        );


                    node.className =
                        "workflow-step-node success";


                    node.textContent =
                        index + 1;


                    const content =
                        document.createElement(
                            "div"
                        );


                    content.className =
                        "workflow-step-content";


                    const text =
                        document.createElement(
                            "div"
                        );


                    const label =
                        step.label ||
                        getToolLabel(
                            step.tool
                        );


                    const description =
                        getStepDescription(
                            step.tool
                        );


                    text.innerHTML = `
                        <div class="workflow-step-name">
                            ${escapeHtml(label)}
                        </div>

                        <div class="workflow-step-description">
                            ${escapeHtml(description)}
                        </div>
                    `;


                    const meta =
                        document.createElement(
                            "div"
                        );


                    meta.className =
                        "workflow-step-meta";


                    const statusElement =
                        document.createElement(
                            "div"
                        );


                    statusElement.className =
                        "workflow-success";


                    statusElement.textContent =
                        "✓ " +
                        getStatusLabel(
                            step.status
                        );


                    const duration =
                        document.createElement(
                            "div"
                        );


                    duration.className =
                        "workflow-duration";


                    duration.textContent =
                        formatDuration(
                            step.duration_ms
                        );


                    meta.appendChild(
                        statusElement
                    );


                    meta.appendChild(
                        duration
                    );


                    content.appendChild(
                        text
                    );


                    content.appendChild(
                        meta
                    );


                    item.appendChild(
                        node
                    );


                    item.appendChild(
                        content
                    );


                    container.appendChild(
                        item
                    );

                }
            );

        }
    );

}


/* =====================================================
   25. Workflow Step Description
===================================================== */

function getStepDescription(tool) {

    const descriptions = {

        agent_planning:
            "理解用户意图并规划 Agent 执行路径",

        knowledge_search:
            "从企业差旅知识库检索相关制度",

        calculate_travel_expense:
            "根据企业制度计算住宿、伙食等差旅费用",

        calculator:
            "执行数学运算并校验费用结果",

        final_answer:
            "整合检索结果与工具结果生成最终回答"

    };


    return (
        descriptions[tool] ||
        "Agent Tool 执行任务"
    );

}


/* =====================================================
   26. Tool Label
===================================================== */

function getToolLabel(tool) {

    const labels = {

        agent_planning:
            "任务规划",

        knowledge_search:
            "知识库检索",

        calculator:
            "费用计算",

        calculate_travel_expense:
            "差旅费用计算",

        final_answer:
            "生成最终回答"

    };


    return (
        labels[tool] ||
        tool ||
        "Agent Tool"
    );

}


/* =====================================================
   27. Status Label
===================================================== */

function getStatusLabel(status) {

    const labels = {

        success:
            "执行成功",

        completed:
            "执行成功",

        running:
            "执行中",

        error:
            "执行失败"

    };


    return (
        labels[status] ||
        "执行成功"
    );

}


/* =====================================================
   28. Workflow Error
===================================================== */

function renderWorkflowError(
    message
) {

    const containers = [

        document.getElementById(
            "workflowSteps"
        ),

        document.getElementById(
            "agentSteps"
        )

    ];


    containers.forEach(
        function (container) {

            if (!container) {

                return;

            }


            container.innerHTML = `

                <div class="workflow-error-box">

                    <div class="workflow-error-title">
                        Agent 执行失败
                    </div>

                    <div class="workflow-error-desc">
                        ${escapeHtml(
                            message ||
                            "未知错误"
                        )}
                    </div>

                </div>

            `;

        }
    );

}


/* =====================================================
   29. Workflow Page
===================================================== */

async function loadWorkflow() {

    /*
       如果当前已经有 Agent 执行记录，
       优先显示当前会话记录。
    */

    if (
        lastWorkflowSteps &&
        lastWorkflowSteps.length > 0
    ) {

        renderWorkflowSteps(
            lastWorkflowSteps,
            "COMPLETED"
        );

        setText(
            "workflowStatus",
            "COMPLETED"
        );

        return;

    }


    /*
       否则从后端读取默认 Workflow。
    */

    try {

        const response =
            await fetch(
                "/api/workflow"
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                "Workflow 数据加载失败"
            );

        }


        const workflowSteps =
            normalizeSteps(
                data.workflow?.steps ||
                []
            );


        renderWorkflowSteps(
            workflowSteps,
            "COMPLETED"
        );


        setText(
            "workflowStatus",
            "READY"
        );


    } catch (error) {

        console.error(
            "Workflow 加载失败：",
            error
        );


        /*
           后端 Workflow 没有数据时，
           不让页面出现错误红框，
           而是保持漂亮的空状态。
        */

        renderWorkflowSteps(
            [],
            "COMPLETED"
        );

    }

}


/* =====================================================
   30. Sources
===================================================== */

function renderSources(sources) {

    const container =
        document.getElementById(
            "agentSources"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    if (
        !sources ||
        sources.length === 0
    ) {

        container.innerHTML = `
            <div class="conversation-empty">
                本次回答未返回知识库来源
            </div>
        `;

        return;

    }


    sources.forEach(
        function (source) {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "conversation";


            const title =
                source.title ||
                "企业知识库";


            const sourceName =
                source.source ||
                "";


            const section =
                source.section ||
                "";


            const distance =
                Number(
                    source.distance ?? 0
                ).toFixed(4);


            item.innerHTML = `

                <div class="conversation-question">

                    ${escapeHtml(title)}

                </div>


                <div class="conversation-time">

                    ${escapeHtml(sourceName)}

                    ${section ? " · " : ""}

                    ${escapeHtml(section)}

                    · Distance:
                    ${distance}

                </div>

            `;


            container.appendChild(
                item
            );

        }
    );

}


/* =====================================================
   31. Agent Status
===================================================== */

function showAgentStatus(text) {

    setText(
        "agentStatusText",
        text
    );

}


/* =====================================================
   32. Sessions
===================================================== */

async function loadSessions() {

    try {

        const response =
            await fetch(
                "/api/sessions"
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                "Sessions 数据加载失败"
            );

        }


        sessions =
            data.sessions || [];


        renderSessions(
            sessions
        );


        renderDashboardSessions(
            sessions
        );


    } catch (error) {

        console.error(
            "Sessions 加载失败：",
            error
        );

    }

}


/* =====================================================
   33. Render Sessions
===================================================== */

function renderSessions(items) {

    const container =
        document.getElementById(
            "sessionList"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    if (
        !items ||
        items.length === 0
    ) {

        container.innerHTML = `
            <div class="workflow-empty">

                <div class="workflow-empty-icon">
                    ◷
                </div>

                <div>
                    暂无最近会话
                </div>

                <div class="workflow-empty-desc">
                    与 Agent 对话后，会话记录会显示在这里
                </div>

            </div>
        `;

        return;

    }


    items.forEach(
        function (session) {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "conversation";


            item.innerHTML = `

                <div class="conversation-question">

                    ${escapeHtml(
                        session.question || ""
                    )}

                </div>


                <div class="conversation-time">

                    ${formatDuration(
                        session.duration_ms
                    )}

                </div>

            `;


            container.appendChild(
                item
            );

        }
    );

}


/* =====================================================
   34. Quick Actions
===================================================== */

function initializeQuickActions() {

    const buttons =
        document.querySelectorAll(
            ".quick-button"
        );


    buttons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                async function () {

                    const question =
                        button.dataset.question;


                    if (!question) {

                        return;

                    }


                    await loadPage("agent");


                    const input =
                        document.getElementById(
                            "question"
                        );


                    if (input) {

                        input.value =
                            question;


                        input.focus();

                    }

                }
            );

        }
    );

}


/* =====================================================
   35. Format Answer
===================================================== */

function formatAnswer(text) {

    if (!text) {

        return "";

    }


    let result =
        escapeHtml(text);


    /*
       Markdown Bold
    */

    result =
        result.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    /*
       Markdown Bullet
    */

    result =
        result.replace(
            /^- (.*)$/gm,
            "• $1"
        );


    /*
       New line
    */

    result =
        result.replace(
            /\n/g,
            "<br>"
        );


    return result;

}


/* =====================================================
   36. Escape HTML
===================================================== */

function escapeHtml(text) {

    if (
        text === undefined ||
        text === null
    ) {

        return "";

    }


    return String(text)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


/* =====================================================
   37. Text Helper
===================================================== */

function setText(
    id,
    value
) {

    const element =
        document.getElementById(
            id
        );


    if (element) {

        element.textContent =
            value;

    }

}


/* =====================================================
   38. Duration
===================================================== */

function formatDuration(
    milliseconds
) {

    if (
        milliseconds === undefined ||
        milliseconds === null
    ) {

        return "-";

    }


    const ms =
        Number(milliseconds);


    if (
        Number.isNaN(ms)
    ) {

        return "-";

    }


    if (
        ms < 1000
    ) {

        return `${ms} ms`;

    }


    return (
        (ms / 1000).toFixed(1)
        +
        " s"
    );

}


/* =====================================================
   39. Message ID
===================================================== */

function createMessageId() {

    return (
        "message-" +
        Date.now() +
        "-" +
        Math.random()
            .toString(36)
            .substring(2, 8)
    );

}