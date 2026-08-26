/* =========================================================
   东方智行 · Enterprise AI Workbench
   Main JavaScript
========================================================= */


/* =========================================================
   1. 页面配置
========================================================= */

const pageTitles = {

    dashboard: [
        "工作台",
        "企业 AI 能力与智能业务入口"
    ],

    knowledge: [
        "企业知识库",
        "企业制度、业务规则与结构化知识的统一入口"
    ],

    agent: [
        "AI Agent",
        "企业业务智能体与 Tool 调用能力"
    ],

    workflow: [
        "Workflow",
        "实时观察 Agent 任务执行过程"
    ],

    chat: [
        "企业差旅助手",
        "与企业 AI Agent 进行自然语言交互"
    ]

};


/* =========================================================
   2. 最近会话
========================================================= */

let recentConversations = [];


/* =========================================================
   3. 页面切换
========================================================= */

function switchPage(pageName) {

    const pages =
        document.querySelectorAll(
            ".page"
        );


    pages.forEach(
        function(page) {

            page.classList.remove(
                "active"
            );

        }
    );


    const targetPage =
        document.getElementById(
            pageName
        );


    if (targetPage) {

        targetPage.classList.add(
            "active"
        );

    }


    const navItems =
        document.querySelectorAll(
            ".nav-item"
        );


    navItems.forEach(
        function(item) {

            item.classList.remove(
                "active"
            );


            if (
                item.dataset.page ===
                pageName
            ) {

                item.classList.add(
                    "active"
                );

            }

        }
    );


    if (
        pageTitles[pageName]
    ) {

        document.getElementById(
            "pageTitle"
        ).textContent =
            pageTitles[pageName][0];


        document.getElementById(
            "pageDescription"
        ).textContent =
            pageTitles[pageName][1];

    }


    /* ==================================================
       进入 Workflow 页面时
       保留当前 Agent Trace
    ================================================== */

    if (
        pageName === "workflow"
    ) {

        updateWorkflowStatus();

    }

}


/* =========================================================
   4. 绑定导航
========================================================= */

document
    .querySelectorAll(
        ".nav-item"
    )
    .forEach(
        function(item) {

            item.addEventListener(
                "click",
                function() {

                    switchPage(
                        item.dataset.page
                    );

                }
            );

        }
    );


/* =========================================================
   5. DOM
========================================================= */

const questionInput =
    document.getElementById(
        "question"
    );


const sendButton =
    document.getElementById(
        "sendButton"
    );


const chatMessages =
    document.getElementById(
        "chatMessages"
    );


/* =========================================================
   6. Workflow Tool 名称
========================================================= */

function getWorkflowToolName(
    tool
) {

    const names = {

        agent_planning:
            "Agent Planning",

        knowledge_search:
            "Knowledge Search",

        calculator:
            "Calculator",

        calculate_travel_expense:
            "Travel Expense Calculator",

        final_answer:
            "Final Answer"

    };


    return (
        names[tool]
        ||
        "Agent Step"
    );

}


/* =========================================================
   7. Workflow Tool 描述
========================================================= */

function getWorkflowDescription(
    tool
) {

    const descriptions = {

        agent_planning:
            "分析用户任务并决定执行策略",

        knowledge_search:
            "检索企业差旅制度与知识",

        calculator:
            "执行数学表达式计算",

        calculate_travel_expense:
            "计算差旅费用",

        final_answer:
            "整合工具结果并生成最终回答"

    };


    return (
        descriptions[tool]
        ||
        "Agent 执行步骤"
    );

}


/* =========================================================
   8. Workflow Status
========================================================= */

function updateWorkflowStatus(
    status = "IDLE"
) {

    const element =
        document.getElementById(
            "workflowStatus"
        );


    if (!element) {

        return;

    }


    element.textContent =
        status;

}


/* =========================================================
   9. Workflow Monitor
========================================================= */

function renderWorkflow(
    steps,
    totalDuration = 0
) {

    const monitor =
        document.getElementById(
            "workflowMonitor"
        );


    if (!monitor) {

        return;

    }


    if (
        !steps ||
        steps.length === 0
    ) {

        monitor.innerHTML = `

            <div class="workflow-empty">

                <div class="workflow-empty-icon">
                    ◇
                </div>

                <div>
                    等待 Agent 执行
                </div>

                <div class="workflow-empty-desc">
                    在企业差旅助手中提交问题后，
                    Agent 执行轨迹将在这里显示
                </div>

            </div>

        `;

        updateWorkflowStatus(
            "IDLE"
        );

        return;

    }


    monitor.innerHTML = "";


    steps.forEach(
        function(step, index) {

            const toolName =
                getWorkflowToolName(
                    step.tool
                );


            const description =
                getWorkflowDescription(
                    step.tool
                );


            const status =
                step.status ||
                "success";


            const duration =
                Number.isFinite(
                    Number(
                        step.duration_ms
                    )
                )
                    ? `${step.duration_ms} ms`
                    : "";


            const statusHTML =
                status === "success"

                    ? `
                        <span class="workflow-success">
                            ✓ Success
                        </span>
                    `

                    : `
                        <span class="workflow-error">
                            ✕ Error
                        </span>
                    `;


            const nodeClass =
                status === "success"
                    ? "workflow-step-node success"
                    : "workflow-step-node error";


            const stepHTML = `

                <div class="workflow-step">

                    <div
                        class="${nodeClass}"
                    >
                        ${index + 1}
                    </div>


                    <div class="workflow-step-content">

                        <div>

                            <div
                                class="workflow-step-name"
                            >
                                ${escapeHTML(
                                    toolName
                                )}
                            </div>

                            <div
                                class="workflow-step-description"
                            >
                                ${escapeHTML(
                                    description
                                )}
                            </div>

                        </div>


                        <div class="workflow-step-meta">

                            ${statusHTML}

                            <span
                                class="workflow-duration"
                            >
                                ${escapeHTML(
                                    duration
                                )}
                            </span>

                        </div>

                    </div>

                </div>

            `;


            monitor.innerHTML +=
                stepHTML;

        }
    );


    /* ==================================================
       Workflow Summary
    ================================================== */

    const successCount =
        steps.filter(
            function(step) {

                return (
                    step.status ===
                    "success"
                );

            }
        ).length;


    updateWorkflowStatus(
        `COMPLETED · ${successCount}/${steps.length} STEPS · ${totalDuration} ms`
    );

}


/* =========================================================
   10. Workflow Loading
========================================================= */

function renderWorkflowLoading() {

    const monitor =
        document.getElementById(
            "workflowMonitor"
        );


    if (!monitor) {

        return;

    }


    updateWorkflowStatus(
        "RUNNING"
    );


    monitor.innerHTML = `

        <div class="workflow-running">

            <div class="workflow-loading-spinner"></div>

            <div>

                <div class="workflow-running-title">
                    Agent 正在执行任务
                </div>

                <div class="workflow-running-desc">
                    正在分析问题并调用相关工具……
                </div>

            </div>

        </div>

    `;

}


/* =========================================================
   11. 最近会话
========================================================= */

function addRecentConversation(
    question
) {

    recentConversations.unshift({

        question:
            question,

        time:
            "刚刚",

        agent:
            "企业差旅助手"

    });


    recentConversations =
        recentConversations.slice(
            0,
            5
        );


    renderRecentConversations();

}


/* =========================================================
   12. 渲染最近会话
========================================================= */

function renderRecentConversations() {

    const container =
        document.getElementById(
            "recentConversations"
        );


    if (!container) {

        return;

    }


    if (
        recentConversations.length ===
        0
    ) {

        container.innerHTML = `

            <div class="conversation-empty">
                暂无最近会话
            </div>

        `;

        return;

    }


    container.innerHTML = "";


    recentConversations.forEach(
        function(item) {

            const element =
                document.createElement(
                    "div"
                );


            element.className =
                "conversation";


            element.innerHTML = `

                <div class="conversation-question">
                    ${escapeHTML(
                        item.question
                    )}
                </div>

                <div class="conversation-time">
                    ${escapeHTML(
                        item.time
                    )}
                    ·
                    ${escapeHTML(
                        item.agent
                    )}
                </div>

            `;


            element.addEventListener(
                "click",
                function() {

                    questionInput.value =
                        item.question;

                    switchPage(
                        "chat"
                    );

                    questionInput.focus();

                }
            );


            container.appendChild(
                element
            );

        }
    );

}


/* =========================================================
   13. Chat
========================================================= */

async function sendQuestion() {

    const question =
        questionInput.value.trim();


    if (!question) {

        return;

    }


    /* ==================================================
       防止重复发送
    ================================================== */

    if (
        sendButton.disabled
    ) {

        return;

    }


    sendButton.disabled =
        true;


    sendButton.textContent =
        "处理中";


    /* ==================================================
       显示用户消息
    ================================================== */

    chatMessages.innerHTML += `

        <div class="message user">

            <div class="message-bubble">

                ${escapeHTML(
                    question
                )}

            </div>

        </div>

    `;


    questionInput.value =
        "";


    /* ==================================================
       Workflow Loading
    ================================================== */

    renderWorkflowLoading();


    /* ==================================================
       Loading Message
    ================================================== */

    const loadingId =
        "loading-" +
        Date.now();


    chatMessages.innerHTML += `

        <div
            class="message ai"
            id="${loadingId}"
        >

            <div class="message-bubble">

                <div class="ai-thinking">

                    <span></span>
                    <span></span>
                    <span></span>

                    正在调用企业 Agent……

                </div>

            </div>

        </div>

    `;


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    try {

        /* ==================================================
           API
        ================================================== */

        const response =
            await fetch(
                "/chat",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            message:
                                question

                        })

                }
            );


        const data =
            await response.json();


        /* ==================================================
           移除 Loading
        ================================================== */

        const loading =
            document.getElementById(
                loadingId
            );


        if (loading) {

            loading.remove();

        }


        /* ==================================================
           请求失败
        ================================================== */

        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(

                data.message ||
                "请求失败"

            );

        }


        /* ==================================================
           更新 Workflow
        ================================================== */

        renderWorkflow(

            data.steps,

            data.total_duration_ms

        );


        /* ==================================================
           参考来源
        ================================================== */

        let sourceHTML = "";


        if (
            data.sources &&
            data.sources.length > 0
        ) {

            sourceHTML = `

                <div class="source-box">

                    <strong>
                        📚 参考来源
                    </strong>

                    <br>

            `;


            data.sources.forEach(
                function(source) {

                    sourceHTML += `

                        ${escapeHTML(
                            source.source ||
                            ""
                        )}

                        ·

                        ${escapeHTML(
                            source.section ||
                            ""
                        )}

                        <br>

                    `;

                }
            );


            sourceHTML += `

                </div>

            `;

        }


        /* ==================================================
           执行信息
        ================================================== */

        const executionHTML = `

            <div class="execution-meta">

                Agent Execution

                ·

                ${escapeHTML(
                    String(
                        data.total_duration_ms ||
                        0
                    )
                )}

                ms

            </div>

        `;


        /* ==================================================
           AI Answer
        ================================================== */

        chatMessages.innerHTML += `

            <div class="message ai">

                <div class="message-bubble">

                    ${escapeHTML(
                        data.answer ||
                        ""
                    )}

                    ${sourceHTML}

                    ${executionHTML}

                </div>

            </div>

        `;


        /* ==================================================
           最近会话
        ================================================== */

        addRecentConversation(
            question
        );


        /* ==================================================
           Dashboard 更新
        ================================================== */

        updateDashboard();


    }
    catch (error) {

        /* ==================================================
           移除 Loading
        ================================================== */

        const loading =
            document.getElementById(
                loadingId
            );


        if (loading) {

            loading.remove();

        }


        /* ==================================================
           Workflow Error
        ================================================== */

        updateWorkflowStatus(
            "ERROR"
        );


        const monitor =
            document.getElementById(
                "workflowMonitor"
            );


        if (monitor) {

            monitor.innerHTML = `

                <div class="workflow-error-box">

                    <div class="workflow-error-title">
                        Agent 执行失败
                    </div>

                    <div class="workflow-error-desc">
                        ${escapeHTML(
                            error.message
                        )}
                    </div>

                </div>

            `;

        }


        /* ==================================================
           AI Error Message
        ================================================== */

        chatMessages.innerHTML += `

            <div class="message ai">

                <div class="message-bubble">

                    AI 暂时无法完成请求。

                    <br><br>

                    ${escapeHTML(
                        error.message
                    )}

                </div>

            </div>

        `;

    }
    finally {

        /* ==================================================
           恢复发送按钮
        ================================================== */

        sendButton.disabled =
            false;


        sendButton.textContent =
            "发送";


        chatMessages.scrollTop =
            chatMessages.scrollHeight;

    }

}


/* =========================================================
   14. Dashboard
========================================================= */

function updateDashboard() {

    const countElement =
        document.getElementById(
            "conversationCount"
        );


    if (
        countElement
    ) {

        countElement.textContent =
            recentConversations.length;

    }

}


/* =========================================================
   15. 发送按钮
========================================================= */

sendButton.addEventListener(
    "click",
    sendQuestion
);


/* =========================================================
   16. Enter
========================================================= */

questionInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key ===
            "Enter"
        ) {

            event.preventDefault();

            sendQuestion();

        }

    }
);


/* =========================================================
   17. HTML 安全处理
========================================================= */

function escapeHTML(
    text
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        text == null
            ? ""
            : String(text);


    return div.innerHTML;

}


/* =========================================================
   18. 初始化
========================================================= */

renderRecentConversations();

updateWorkflowStatus(
    "IDLE"
);