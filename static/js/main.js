// Custom JavaScript for dynamic functionality

document.addEventListener("DOMContentLoaded", function() {
    // Add new skill entry dynamically
    var addSkillButton = document.getElementById("add-skill");
    if (addSkillButton) {
        addSkillButton.addEventListener("click", function() {
            var skillSection = document.getElementById("skills-section");
            var newSkill = document.createElement("div");
            newSkill.classList.add("skill-entry", "fade-in");
            newSkill.innerHTML = `
                <label for="skills[]" class="form-label">Skill:</label>
                <input type="text" name="skills[]" class="form-control" required placeholder="e.g., Python, Java">
            `;
            skillSection.appendChild(newSkill);
        });
    }

    // Add new education entry dynamically
    var addEducationButton = document.getElementById("add-education");
    if (addEducationButton) {
        addEducationButton.addEventListener("click", function() {
            var educationSection = document.getElementById("education-section");
            var newEducation = document.createElement("div");
            newEducation.classList.add("education-entry", "fade-in");
            newEducation.innerHTML = `
                <label for="level[]" class="form-label">Education Level:</label>
                <input type="text" name="level[]" class="form-control" required placeholder="e.g., 10th, 12th, B.Tech">
                
                <label for="subject[]" class="form-label">Subject:</label>
                <input type="text" name="subject[]" class="form-control" required placeholder="e.g., Science, Mathematics">
                
                <label for="stream[]" class="form-label">Stream (if applicable):</label>
                <input type="text" name="stream[]" class="form-control" placeholder="e.g., Computer Science">
                
                <label for="grade[]" class="form-label">Grade (Percentage or CGPA):</label>
                <input type="text" name="grade[]" class="form-control" required placeholder="e.g., 85%, 9.2 CGPA">
                
                <label for="year[]" class="form-label">Passing Year:</label>
                <input type="text" name="year[]" class="form-control" required placeholder="e.g., 2022">
            `;
            educationSection.appendChild(newEducation);
        });
    }
});
