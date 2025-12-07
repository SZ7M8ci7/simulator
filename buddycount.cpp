#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include <nlohmann/json.hpp>

struct Card {
    std::string rare;
    std::string chara;
    std::string buddy1c;
    std::string buddy2c;
    std::string buddy3c;
    std::string name;
};

std::vector<Card> load_cards(const std::string& path) {
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error("Failed to open file: " + path);
    }

    nlohmann::json data;
    in >> data;

    std::vector<Card> cards;
    cards.reserve(data.size());

    for (const auto& item : data) {
        Card c;
        c.rare = item.value("rare", "");
        if (c.rare != "SR" && c.rare != "SSR") {
            continue;
        }
        c.chara = item.value("chara", "");
        c.buddy1c = item.value("buddy1c", "");
        c.buddy2c = item.value("buddy2c", "");
        c.buddy3c = item.value("buddy3c", "");
        c.name = item.value("name", "");
        cards.push_back(std::move(c));
    }

    return cards;
}

int main() {
    try {
        const auto cards = load_cards("chara.json");
        const std::size_t N = cards.size();

        for (std::size_t i = 0; i < N; ++i) {
            for (std::size_t j = i + 1; j < N; ++j) {
                for (std::size_t k = j + 1; k < N; ++k) {
                    for (std::size_t l = k + 1; l < N; ++l) {
                        const Card* member_ptrs[4] = {&cards[i], &cards[j], &cards[k], &cards[l]};

                        std::unordered_set<std::string> member_name_set{
                            member_ptrs[0]->chara, member_ptrs[1]->chara, member_ptrs[2]->chara, member_ptrs[3]->chara};

                        int buddy = 0;
                        std::unordered_map<std::string, int> missing_counts;

                        auto add_buddy = [&](const std::string& buddy_name) {
                            if (member_name_set.count(buddy_name)) {
                                ++buddy;
                            } else {
                                ++missing_counts[buddy_name];
                            }
                        };

                        for (const Card* mem : member_ptrs) {
                            add_buddy(mem->buddy1c);
                            add_buddy(mem->buddy2c);
                            add_buddy(mem->buddy3c);
                        }

                        if (buddy <= 6) {
                            continue;
                        }

                        for (const auto& candidate : cards) {
                            int tmp = 0;
                            if (member_name_set.count(candidate.buddy1c)) {
                                ++tmp;
                            }
                            if (member_name_set.count(candidate.buddy2c)) {
                                ++tmp;
                            }
                            if (member_name_set.count(candidate.buddy3c)) {
                                ++tmp;
                            }

                            const int missing = missing_counts.count(candidate.chara)
                                                    ? missing_counts.at(candidate.chara)
                                                    : 0;

                            if (buddy + missing + tmp > 12) {
                                std::vector<std::string> names = {
                                    member_ptrs[0]->name,
                                    member_ptrs[1]->name,
                                    member_ptrs[2]->name,
                                    member_ptrs[3]->name,
                                    candidate.name};
                                std::sort(names.begin(), names.end());

                                for (std::size_t idx = 0; idx < names.size(); ++idx) {
                                    if (idx > 0) {
                                        std::cout << ",";
                                    }
                                    std::cout << names[idx];
                                }
                                std::cout << std::endl;
                                return 0;
                            }
                        }
                    }
                }
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
