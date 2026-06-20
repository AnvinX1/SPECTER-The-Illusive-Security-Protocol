use anyhow::Result;
use crossterm::{
    event::{self, Event, KeyCode, KeyEventKind},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    layout::{Alignment, Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style, Stylize},
    text::{Line, Span},
    widgets::{Block, Borders, Clear, List, ListItem, Paragraph, Wrap},
    DefaultTerminal, Frame,
};
use specter_llm::LlmConfig;
use std::{io, time::Duration};

#[derive(Debug)]
struct ConsoleState {
    input: String,
    selected_mode: usize,
    activity: Vec<&'static str>,
    llm: LlmConfig,
}

impl ConsoleState {
    fn new(llm: LlmConfig) -> Self {
        let activity = if llm.api_key_present() || llm.api_key_env.is_none() {
            vec![
                "CERBERUS_CORE loaded Specter Toolkit manifests",
                "POLICY_ENGINE classified passive actions as allowed",
                "LLM_CONNECTOR provider configured",
                "AGENT_RUNTIME waiting for operator mission",
            ]
        } else {
            vec![
                "CERBERUS_CORE loaded Specter Toolkit manifests",
                "POLICY_ENGINE classified passive actions as allowed",
                "LLM_CONNECTOR provider selected but API key missing",
                "AGENT_RUNTIME waiting for operator mission",
            ]
        };

        Self {
            input: String::new(),
            selected_mode: 0,
            activity,
            llm,
        }
    }
}

pub fn run(llm: LlmConfig) -> Result<()> {
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let mut terminal = ratatui::init();
    let mut state = ConsoleState::new(llm);

    let result = run_loop(&mut terminal, &mut state);

    ratatui::restore();
    disable_raw_mode()?;
    execute!(io::stdout(), LeaveAlternateScreen)?;

    result
}

fn run_loop(terminal: &mut DefaultTerminal, state: &mut ConsoleState) -> Result<()> {
    loop {
        terminal.draw(|frame| render(frame, state))?;

        if event::poll(Duration::from_millis(120))? {
            if let Event::Key(key) = event::read()? {
                if key.kind != KeyEventKind::Press {
                    continue;
                }

                match key.code {
                    KeyCode::Char('q') if state.input.is_empty() => break,
                    KeyCode::Esc => break,
                    KeyCode::Tab => state.selected_mode = (state.selected_mode + 1) % 4,
                    KeyCode::Backspace => {
                        state.input.pop();
                    }
                    KeyCode::Enter => {
                        if !state.input.trim().is_empty() {
                            state
                                .activity
                                .push("OPERATOR mission queued for governed planning");
                            state.input.clear();
                        }
                    }
                    KeyCode::Char(ch) => state.input.push(ch),
                    _ => {}
                }
            }
        }
    }

    Ok(())
}

fn render(frame: &mut Frame<'_>, state: &ConsoleState) {
    let area = frame.area();
    frame.render_widget(Clear, area);

    let root = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(5),
            Constraint::Min(22),
            Constraint::Length(5),
        ])
        .split(area);

    render_header(frame, root[0], state);
    render_body(frame, root[1], state);
    render_input(frame, root[2], state);
}

fn render_header(frame: &mut Frame<'_>, area: Rect, state: &ConsoleState) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Length(34),
            Constraint::Min(20),
            Constraint::Length(34),
        ])
        .split(area);

    let logo = Paragraph::new(vec![
        Line::from(Span::styled(
            "CERBERUS",
            Style::default()
                .fg(Color::Black)
                .add_modifier(Modifier::BOLD),
        )),
        Line::from(Span::styled(
            "ARASKOVA LABS / SECURITY OPS",
            Style::default().fg(Color::DarkGray),
        )),
    ])
    .block(
        Block::default()
            .borders(Borders::ALL)
            .border_style(Color::Gray),
    );

    let status = Paragraph::new(vec![
        Line::from("RUST-NATIVE AGENTIC SECURITY CONSOLE").centered(),
        Line::from(vec![
            Span::styled("MODEL: ", Style::default().fg(Color::DarkGray)),
            Span::styled(
                state.llm.provider.to_string().to_uppercase(),
                Style::default().fg(Color::Black).bold(),
            ),
            Span::raw("   "),
            Span::styled("POLICY: ", Style::default().fg(Color::DarkGray)),
            Span::styled("GUARDED", Style::default().fg(Color::Black).bold()),
            Span::raw("   "),
            Span::styled("SCOPE: ", Style::default().fg(Color::DarkGray)),
            Span::styled("LOCAL", Style::default().fg(Color::Black).bold()),
        ])
        .centered(),
        Line::from(vec![
            Span::styled("MODEL: ", Style::default().fg(Color::DarkGray)),
            Span::styled(&state.llm.model, Style::default().fg(Color::Black)),
        ])
        .centered(),
    ])
    .alignment(Alignment::Center)
    .block(
        Block::default()
            .borders(Borders::ALL)
            .border_style(Color::Gray),
    );

    let operator = Paragraph::new(vec![
        Line::from("ANVIN").right_aligned(),
        Line::from("ADMIN / OPERATOR").right_aligned(),
    ])
    .block(
        Block::default()
            .borders(Borders::ALL)
            .border_style(Color::Gray),
    );

    frame.render_widget(logo, chunks[0]);
    frame.render_widget(status, chunks[1]);
    frame.render_widget(operator, chunks[2]);
}

fn render_body(frame: &mut Frame<'_>, area: Rect, state: &ConsoleState) {
    let columns = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Length(30),
            Constraint::Min(44),
            Constraint::Length(36),
        ])
        .split(area);

    render_modes(frame, columns[0], state);
    render_activity(frame, columns[1], state);
    render_policy(frame, columns[2]);
}

fn render_modes(frame: &mut Frame<'_>, area: Rect, state: &ConsoleState) {
    let modes = [
        ("01", "Recon"),
        ("02", "Code Audit"),
        ("03", "Exploit Validation"),
        ("04", "Fix + Verify"),
    ];

    let items = modes
        .iter()
        .enumerate()
        .map(|(index, (num, label))| {
            let style = if index == state.selected_mode {
                Style::default()
                    .fg(Color::Black)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::DarkGray)
            };
            ListItem::new(Line::from(vec![
                Span::styled(*num, Style::default().fg(Color::DarkGray)),
                Span::raw("  "),
                Span::styled(*label, style),
            ]))
        })
        .collect::<Vec<_>>();

    let list = List::new(items).block(
        Block::default()
            .title(" MODES ")
            .borders(Borders::ALL)
            .border_style(Color::Gray),
    );

    frame.render_widget(list, area);
}

fn render_activity(frame: &mut Frame<'_>, area: Rect, state: &ConsoleState) {
    let items = state
        .activity
        .iter()
        .rev()
        .take(12)
        .map(|entry| {
            ListItem::new(Line::from(vec![
                Span::styled(">", Style::default().fg(Color::Rgb(231, 63, 7))),
                Span::raw(" "),
                Span::styled(*entry, Style::default().fg(Color::Black)),
            ]))
        })
        .collect::<Vec<_>>();

    let list = List::new(items).block(
        Block::default()
            .title(" LIVE OPERATIONS ")
            .borders(Borders::ALL)
            .border_style(Color::Gray),
    );

    frame.render_widget(list, area);
}

fn render_policy(frame: &mut Frame<'_>, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(9),
            Constraint::Length(9),
            Constraint::Min(5),
        ])
        .split(area);

    let gates = Paragraph::new(vec![
        Line::from("PASSIVE             ALLOW"),
        Line::from("ACTIVE SAFE         APPROVAL"),
        Line::from("INTRUSIVE           APPROVAL"),
        Line::from("EXPLOIT VALIDATION  APPROVAL"),
        Line::from("FORBIDDEN           DENY"),
    ])
    .block(
        Block::default()
            .title(" POLICY GATES ")
            .borders(Borders::ALL)
            .border_style(Color::Gray),
    );

    let modules = Paragraph::new(vec![
        Line::from("Specter Toolkit bridge"),
        Line::from("Rust policy core"),
        Line::from("Findings engine"),
        Line::from("Evidence vault"),
        Line::from("Agent runtime"),
    ])
    .block(
        Block::default()
            .title(" MODULES ")
            .borders(Borders::ALL)
            .border_style(Color::Gray),
    );

    let help = Paragraph::new(vec![
        Line::from("TAB  cycle mode"),
        Line::from("ENTER queue mission"),
        Line::from("ESC/q exit"),
    ])
    .wrap(Wrap { trim: true })
    .block(
        Block::default()
            .title(" CONTROL ")
            .borders(Borders::ALL)
            .border_style(Color::Gray),
    );

    frame.render_widget(gates, chunks[0]);
    frame.render_widget(modules, chunks[1]);
    frame.render_widget(help, chunks[2]);
}

fn render_input(frame: &mut Frame<'_>, area: Rect, state: &ConsoleState) {
    let prompt = Paragraph::new(Line::from(vec![
        Span::styled(
            "cerberus",
            Style::default().fg(Color::Rgb(231, 63, 7)).bold(),
        ),
        Span::styled(" > ", Style::default().fg(Color::Black).bold()),
        Span::styled(&state.input, Style::default().fg(Color::Black)),
    ]))
    .block(
        Block::default()
            .title(" MISSION INPUT ")
            .borders(Borders::ALL)
            .border_style(Color::Gray),
    );

    frame.render_widget(prompt, area);
}
